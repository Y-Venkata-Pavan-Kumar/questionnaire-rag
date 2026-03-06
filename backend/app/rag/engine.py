from typing import List, Dict, Optional
import os
import groq
import logging
import traceback
from sentence_transformers import SentenceTransformer
import numpy as np
import logging
logger = logging.getLogger(__name__)
from app.config import settings

logger = logging.getLogger(__name__)
EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
class RAGEngine:
    
    def __init__(self, openai_api_key: Optional[str] = None, api_key: Optional[str] = None):
        self.groq_key = openai_api_key or api_key or os.getenv("GROQ_API_KEY")
        self.documents: List[Dict] = []
        self.client: Optional[groq.Groq] = None
        self.embed_model = EMBED_MODEL
        self.embeddings = []

        if self.groq_key:
            try:
                self.client = groq.Groq(api_key=self.groq_key)
                logger.info("✅ GROQ CONNECTED")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Groq client: {e}")
                self.client = None
        else:
            logger.warning("⚠️ GROQ KEY NOT FOUND — MOCK MODE")

    def create_collection(self, name: str, docs: List[Dict]) -> str:

        self.documents = docs
        texts = [self._extract_text_from_doc(d) for d in docs]

        self.embeddings = self.embed_model.encode(texts)

        logger.info(f"📚 Collection '{name}' created with {len(docs)} chunks")

        return name

    def _extract_text_from_doc(self, doc) -> str:
        if isinstance(doc, dict):

            if "text" in doc and doc["text"]:
                return doc["text"]

            if "content" in doc and doc["content"]:
                return doc["content"]

            if "body" in doc and doc["body"]:
                return doc["body"]

            if "page_content" in doc and doc["page_content"]:
                return doc["page_content"]

            # NEW: handle database documents
            if "file_path" in doc and os.path.exists(doc["file_path"]):
                try:
                    with open(doc["file_path"], "rb") as f:
                        data = f.read().decode("utf-8", errors="ignore")
                        return data
                except:
                    pass

        return ""
    def process_questionnaire(self, questions: List[Dict]):




        results = []

        for i, q in enumerate(questions):

            print("\n--------------------------------")
           
            context = self.build_context()

            

            result = self.answer_question(q["question_text"])

            

            results.append({
                "id": i + 1,
                "question_number": q.get("question_number", i + 1),
                "question_text": q["question_text"],
                "generated_answer": result["answer"],
                "citations": result["citations"],
                "confidence_score": result["confidence_score"],
                "source_snippets": result["source_snippets"],
                "not_found_in_refs": result["not_found"],
                "final_answer": None
            })

        print("====== END DEBUG ======\n")

        return results
    def build_context(self, docs=None):

        if docs is None:
            docs = self.documents

        context = ""

        

        for d in docs[:5]:
            

            if "text" in d and d["text"].strip():
                context += d["text"] + "\n\n"

        if not context.strip():
            print("🔶 Empty context - running LLM without context")
            return ""

        print("Context length:", len(context))

        return context[:3000]
    def retrieve(self, question, top_k=3):

        if not self.embeddings or not self.documents:
            return []

        question_embedding = self.embed_model.encode([question])[0]

        doc_vectors = self.embeddings / np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        query_vector = question_embedding / np.linalg.norm(question_embedding)

        similarities = np.dot(doc_vectors, query_vector)

        top_indices = np.argsort(similarities)[-top_k:][::-1]

        return [self.documents[i] for i in top_indices]
    def create_collection(self, name: str, docs: List[Dict]):

        self.documents = docs

        


        return name
    def answer_question(self, question: str) -> Dict:
        """
        Answer a question using RAG. Returns structured response with full error handling.
        """
        # Validate inputs
       
        if not question or not isinstance(question, str):
            logger.error(f"Invalid question type: {type(question)}")
            return {
                "answer": "Error: Invalid question format",
                "citations": [],
                "confidence_score": 0,
                "source_snippets": [],
                "not_found": True,
                "error": "Invalid question input"
            }

        docs = self.documents
        context = self.build_context(docs)
        
        # Mock mode fallback
        if not self.client:
            logger.warning("🔶 Running in MOCK mode - no LLM available")
            return {
                "answer": "Not found in references. (Mock mode - API key not configured)",
                "citations": [],
                "confidence_score": 0,
                "source_snippets": [],
                "not_found": True
            }

        # Check if we have any context
        if not context.strip():
            logger.warning("🔶 Empty context - running LLM without context")
            context = "No relevant reference documents found."

        prompt = f"""Use ONLY the following context to answer the question. 
If the answer is not present in the context, respond exactly with: "Not found in references."

Context:
{context}

Question: {question}

Provide a concise, accurate answer based solely on the context above."""

        try:
            logger.info(f"🚀 Sending request to Groq for question: {question[:50]}...")
            
            resp = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a precise assistant that answers security questionnaires using only the provided context. Be concise and accurate."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500,
                timeout=30  # Add timeout to prevent hanging
            )
            
            # Safe response parsing with validation
            if not resp or not hasattr(resp, 'choices') or not resp.choices:
                logger.error("❌ Empty or invalid response from Groq API")
                raise ValueError("Empty response from Groq API")
            
            message = resp.choices[0].message
            if not message or not hasattr(message, 'content'):
                logger.error("❌ Malformed response structure from Groq API")
                raise ValueError("Malformed response from Groq API")
            
            answer = message.content.strip()
            logger.info(f"✅ Received answer: {answer[:100]}...")
            
            # Check for "not found" indicators
            not_found_indicators = [
                "not found in references",
                "not present in",
                "no information",
                "cannot answer",
                "not mentioned",
                "not available"
            ]
            is_not_found = any(indicator in answer.lower() for indicator in not_found_indicators)
            logger.debug("Prompt sent to LLM")
            return {
                "answer": answer,
                "citations": [{"document_name": "Reference", "page_number": 1}],
                "confidence_score": 0 if is_not_found else 85,
                "source_snippets": [context[:200]] if context else [],
                "not_found": is_not_found
            }
            
        except groq.APIError as e:
            logger.error(f"❌ Groq API Error: {e}")
            return {
                "answer": f"Error: LLM API issue - {str(e)}",
                "citations": [],
                "confidence_score": 0,
                "source_snippets": [],
                "not_found": True,
                "error": f"Groq API Error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"❌ Unexpected error in answer_question: {e}")
            logger.error(traceback.format_exc())
            return {
                "answer": "Error processing question due to technical issue",
                "citations": [],
                "confidence_score": 0,
                "source_snippets": [],
                "not_found": True,
                "error": f"Unexpected error: {str(e)}"
            }
        

    def process_questionnaire(self, questions: List[Dict]) -> List[Dict]:
        """
        Process multiple questions from a questionnaire with bulletproof error handling.
        """
        # Validate input
        if not questions:
            logger.warning("🔶 Empty questions list provided")
            return []
        
        if not isinstance(questions, list):
            logger.error(f"❌ Expected list of questions, got {type(questions)}: {questions}")
            # Try to handle single question case
            if isinstance(questions, dict):
                questions = [questions]
            else:
                return [{
                    "id": 1,
                    "question_number": 1,
                    "question_text": "[Invalid Input]",
                    "generated_answer": f"Error: Expected list of questions, got {type(questions)}",
                    "citations": [],
                    "confidence_score": 0,
                    "source_snippets": [],
                    "not_found_in_refs": True,
                    "final_answer": None,
                    "error": "Invalid input format"
                }]

        results = []
        
        for i, q in enumerate(questions):
            try:
                # Handle both dict and non-dict items
                if not isinstance(q, dict):
                    logger.warning(f"⚠️ Question {i} is not a dict: {type(q)}")
                    q = {"question_text": str(q)} if q else {"question_text": "[Empty Question]"}

                # Extract question text with multiple fallback keys
                question_text = (
                    q.get("question_text") or 
                    q.get("text") or 
                    q.get("question") or
                    q.get("query") or
                    q.get("content") or
                    str(q) if q else None
                )
                
                if not question_text or not isinstance(question_text, str):
                    logger.warning(f"⚠️ Skipping question {i}: no valid text found. Available keys: {list(q.keys()) if isinstance(q, dict) else 'N/A'}")
                    results.append({
                        "id": i + 1,
                        "question_number": q.get("question_number", i + 1),
                        "question_text": "[Invalid Question Format]",
                        "generated_answer": "Error: Could not extract question text",
                        "citations": [],
                        "confidence_score": 0,
                        "source_snippets": [],
                        "not_found_in_refs": True,
                        "final_answer": None,
                        "error": "Missing or invalid question_text"
                    })
                    continue

                # Process the question
                logger.info(f"📝 Processing question {i+1}: {question_text[:50]}...")
                result = self.answer_question(question_text)
                
                results.append({
                    "id": i + 1,
                    "question_number": q.get("question_number", i + 1),
                    "question_text": question_text,
                    "generated_answer": result.get("answer", "Error: No answer generated"),
                    "citations": result.get("citations", []),
                    "confidence_score": result.get("confidence_score", 0),
                    "source_snippets": result.get("source_snippets", []),
                    "not_found_in_refs": result.get("not_found", True),
                    "final_answer": None,
                    "error": result.get("error")
                })
                
            except Exception as e:
                logger.error(f"❌ Critical error processing question {i}: {e}")
                logger.error(traceback.format_exc())
                results.append({
                    "id": i + 1,
                    "question_number": q.get("question_number", i + 1) if isinstance(q, dict) else i + 1,
                    "question_text": str(q) if not isinstance(q, dict) else "[Processing Error]",
                    "generated_answer": f"Critical error: {str(e)}",
                    "citations": [],
                    "confidence_score": 0,
                    "source_snippets": [],
                    "not_found_in_refs": True,
                    "final_answer": None,
                    "error": str(e)
                })
        
        logger.info(f"✅ Completed processing {len(results)} questions")
        return results

