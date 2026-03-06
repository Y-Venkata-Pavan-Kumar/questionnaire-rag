import sys
sys.path.append('backend')

print("="*60)
print("TESTING ALL MODULES")
print("="*60)

tests = [
    ("Config", "from app.config import settings"),
    ("Database", "from app.database import Base, engine"),
    ("Auth Models", "from app.auth.models import User"),
    ("Auth Utils", "from app.auth.utils import get_password_hash"),
    ("Auth Router", "from app.auth.router import router"),
    ("Document Models", "from app.documents.models import Document"),
    ("Document Processor", "from app.documents.processor import DocumentProcessor"),
    ("Document Chunker", "from app.documents.chunker import TextChunker"),
    ("RAG Engine", "from app.rag.engine import RAGEngine"),
    ("Questionnaire Models", "from app.questionnaires.models import Questionnaire"),
    ("Questionnaire Exporter", "from app.questionnaires.exporter import export_to_docx"),
    ("Main App", "from app.main import app"),
]

passed = 0
failed = 0

for name, import_stmt in tests:
    try:
        exec(import_stmt)
        print(f"✅ {name}")
        passed += 1
    except Exception as e:
        print(f"❌ {name}: {e}")
        failed += 1

print("="*60)
print(f"RESULTS: {passed} passed, {failed} failed")
print("="*60)

if failed == 0:
    print("✅ ALL SYSTEMS READY!")
    print("\nNext step: Run the backend")
    print("Command: cd backend && uvicorn app.main:app --reload")
else:
    print("❌ Fix failed imports before continuing")