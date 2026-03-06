from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
import shutil
import os
import uuid
import logging
logger = logging.getLogger(__name__)
try:
    from backend.app.database import get_db
    from backend.app.auth.router import get_current_user
    from backend.app.documents import models, processor, chunker
    from backend.app.rag.engine import RAGEngine
    from backend.app.config import settings
except ImportError:
    from backend.app.database import get_db
    from backend.app.auth.router import get_current_user
    from backend.app.documents import models, processor, chunker
    from backend.app.rag.engine import RAGEngine
    from backend.app.config import settings

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form("reference"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Check file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in processor.DocumentProcessor.SUPPORTED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
    
    # Save file to disk
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Save to database
    db_doc = models.Document(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        doc_type=doc_type
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    # If reference doc, process for RAG immediately
    if doc_type == "reference":
        try:
            text = processor.DocumentProcessor.extract_text(file_path)

            
            chunker_obj = chunker.TextChunker()
            chunks = chunker_obj.chunk_text(text, file.filename)

            # store chunk metadata
            for c in chunks:
                if "filename" not in c:
                    c["filename"] = file.filename

            collection_name = f"user_{current_user.id}_refs"



            print(f"Stored {len(chunks)} chunks for RAG")
            
        except Exception as e:
            # Don't fail upload if RAG processing fails
            logger.warning(f"RAG processing failed: {e}")
    
    return {
        "document_id": db_doc.id,
        "filename": file.filename,
        "doc_type": doc_type,
        "message": "Upload successful"
    }

@router.get("/list")
async def list_documents(
    doc_type: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List user's documents."""
    query = db.query(models.Document).filter(models.Document.user_id == current_user.id)
    if doc_type:
        query = query.filter(models.Document.doc_type == doc_type)
    
    docs = query.all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "doc_type": d.doc_type,
            "upload_date": d.upload_date
        }
        for d in docs
    ]