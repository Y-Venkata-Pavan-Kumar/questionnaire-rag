# test_imports.py
import sys
sys.path.insert(0, r"C:\Users\yvpaw\OneDrive\Desktop\GTM-AI-Questionaire\questionnaire-rag")

try:
    from app.auth.router import router as auth_router
    print(f"✅ auth_router type: {type(auth_router)}")
    print(f"   Routes: {[r.path for r in auth_router.routes]}")
except Exception as e:
    print(f"❌ auth import failed: {e}")

try:
    from app.documents.router import router as documents_router
    print(f"✅ documents_router type: {type(documents_router)}")
except Exception as e:
    print(f"❌ documents import failed: {e}")

try:
    from app.questionnaires.router import router as questionnaires_router
    print(f"✅ questionnaires_router type: {type(questionnaires_router)}")
    print(f"   Routes: {[r.path for r in questionnaires_router.routes]}")
except Exception as e:
    print(f"❌ questionnaires import failed: {e}")