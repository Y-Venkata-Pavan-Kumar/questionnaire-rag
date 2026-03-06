from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
import shutil
import os
import uuid

# Use consistent imports - always from app
from app.database import get_db
from app.auth.router import get_current_user
from app.documents import processor
from app.rag.engine import RAGEngine
from app.questionnaires import models, exporter
from app.config import settings
from app.documents import models as doc_models
from app.documents.processor import DocumentProcessor

router = APIRouter(prefix="/questionnaires", tags=["questionnaires"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_questionnaire(
    file: UploadFile = File(...),
    title: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Upload and parse questionnaire."""
    # Save file
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Parse questions
    try:
        questions = processor.DocumentProcessor.extract_questions(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse: {str(e)}")
    
    # Create questionnaire record
    db_q = models.Questionnaire(
        user_id=current_user.id,
        title=title,
        original_file=file_path,
        status="uploaded"
    )
    db.add(db_q)
    db.commit()
    db.refresh(db_q)
    
    # Create question records
    for q in questions:
        db_question = models.Question(
            questionnaire_id=db_q.id,
            question_number=q["question_number"],
            question_text=q["question_text"]
        )
        db.add(db_question)
    
    db.commit()
    
    return {
        "questionnaire_id": db_q.id,
        "title": title,
        "total_questions": len(questions)
    }

@router.post("/{q_id}/process")
async def process_questionnaire(
    q_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Process questionnaire with AI."""
    # Verify ownership
    q = db.query(models.Questionnaire).filter(
        models.Questionnaire.id == q_id,
        models.Questionnaire.user_id == current_user.id
    ).first()
    
    if not q:
        raise HTTPException(status_code=404, detail="Not found")
    
    # Get questions
    questions = db.query(models.Question).filter(
        models.Question.questionnaire_id == q_id
    ).all()
    
    questions_data = [
        {"question_number": q.question_number, "question_text": q.question_text}
        for q in questions
    ]
    
    # Get reference documents for the user - use module-level import
    ref_docs = db.query(doc_models.Document).filter(
        doc_models.Document.user_id == current_user.id,
        doc_models.Document.doc_type == "reference"
    ).all()
    
    # Debug: Print found documents
   
    
    # Extract text from reference documents
    reference_texts = []

    for doc in ref_docs:
        try:
            text = DocumentProcessor.extract_text(doc.file_path)

            chunker_obj = chunker.TextChunker()
            chunks = chunker_obj.chunk_text(text, doc.filename)

            reference_texts.extend(chunks)

        except Exception as e:
            print(f"Warning: Could not extract text from {doc.filename}: {e}")
    
    # Process with RAG - load reference documents directly
    api_key = settings.GROQ_API_KEY or settings.OPENAI_API_KEY
    rag = RAGEngine(api_key=api_key)
    from app.documents.models import Document
    from app.documents import processor, chunker

    reference_docs = db.query(Document).filter(
        Document.user_id == current_user.id,
        Document.doc_type == "reference"
    ).all()

    docs = []

    for doc in reference_docs:
        try:
            text = processor.DocumentProcessor.extract_text(doc.file_path)

            chunker_obj = chunker.TextChunker()
            chunks = chunker_obj.chunk_text(text, doc.filename)

            docs.extend(chunks)

        except Exception as e:
            print(f"Error processing document {doc.filename}: {e}")

    print(f"Loaded {len(docs)} chunks into RAG")

    rag.create_collection("user_refs", docs)
    # Debug: Check if Groq client is connected
    if rag.client:
        print(f"✅ Groq client connected! API key starts with: {api_key[:10] if api_key else 'None'}...")
    else:
        print(f"❌ Groq client NOT connected! API key: {api_key[:10] if api_key else 'None'}...")
    
    # Load documents directly into RAG engine
    if reference_texts:
        rag.documents = reference_texts  # Load directly into the engine

    else:
        # No reference documents - warn but continue
        print("Warning: No reference documents found for RAG processing")
    
    try:
        results = rag.process_questionnaire(questions_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    # Save results
    # Update database with results
    for result in results:
        db_q = db.query(models.Question).filter(
            models.Question.questionnaire_id == q_id,
            models.Question.question_number == result["question_number"]
        ).first()
        
        if db_q:
            db_q.generated_answer = result.get("generated_answer") or result.get("answer")
            db_q.confidence_score = result.get("confidence_score", 0)
            db_q.citations = result.get("citations", [])
            db_q.not_found_in_refs = result.get("not_found_in_refs", result.get("not_found", False))
    
    q.status = "completed"
    db.commit()
    
    return {
        "status": "completed",
        "total": len(results),
        "answered": len([r for r in results if not r.get("not_found", r.get("not_found_in_refs", True))]),
        "not_found": len([r for r in results if r.get("not_found", r.get("not_found_in_refs", False))])
    }

@router.get("/{q_id}/review")
async def get_review(
    q_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get questionnaire for review."""
    questions = db.query(models.Question).join(models.Questionnaire).filter(
        models.Question.questionnaire_id == q_id,
        models.Questionnaire.user_id == current_user.id
    ).all()
    
    return [
        {
            "question_id": q.id,
            "question_number": q.question_number,
            "question_text": q.question_text,
            "generated_answer": q.generated_answer,
            "confidence_score": q.confidence_score,
            "citations": q.citations or [],
            "final_answer": q.final_answer,
            "edited_by_user": q.edited_by_user,
            "not_found_in_refs": q.not_found_in_refs
        }
        for q in questions
    ]

@router.post("/{q_id}/update-answer")
async def update_answer(
    q_id: int,
    question_id: int = Form(...),
    final_answer: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update answer after review."""
    question = db.query(models.Question).join(models.Questionnaire).filter(
        models.Question.id == question_id,
        models.Questionnaire.id == q_id,
        models.Questionnaire.user_id == current_user.id
    ).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Not found")
    
    question.final_answer = final_answer
    question.edited_by_user = True
    db.commit()
    
    return {"status": "updated"}

@router.post("/{q_id}/export")
async def export(
    q_id: int,
    format: str = "docx",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Export completed questionnaire."""
    q = db.query(models.Questionnaire).filter(
        models.Questionnaire.id == q_id,
        models.Questionnaire.user_id == current_user.id
    ).first()
    
    if not q:
        raise HTTPException(status_code=404, detail="Not found")
    
    questions = db.query(models.Question).filter(
        models.Question.questionnaire_id == q_id
    ).order_by(models.Question.question_number).all()
    
    export_data = []
    for question in questions:
        export_data.append({
            "question_number": question.question_number,
            "question_text": question.question_text,
            "generated_answer": question.generated_answer,
            "final_answer": question.final_answer or question.generated_answer,
            "citations": question.citations or [],
            "edited_by_user": question.edited_by_user,
            "not_found_in_refs": question.not_found_in_refs
        })
    
    try:
        if format == "docx":
            output_path = exporter.export_to_docx(q.title, export_data)
        elif format == "xlsx":
            output_path = exporter.export_to_excel(q.title, export_data)
        else:
            raise HTTPException(status_code=400, detail="Invalid format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
    
    return FileResponse(
        path=output_path,
        filename=os.path.basename(output_path),
        media_type="application/octet-stream"
    )
@router.get("/list")
async def list_questionnaires(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all questionnaires for user."""
    questionnaires = db.query(models.Questionnaire).filter(
        models.Questionnaire.user_id == current_user.id
    ).order_by(models.Questionnaire.created_at.desc()).all()
    
    return [
        {
            "id": q.id,
            "title": q.title,
            "status": q.status,
            "created_at": q.created_at.isoformat() if q.created_at else None,
            "total_questions": len(q.questions)
        }
        for q in questionnaires
    ]