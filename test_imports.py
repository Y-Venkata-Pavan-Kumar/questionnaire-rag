# test_imports.py - Place this in C:\Users\yvpaw\OneDrive\Desktop\GTM-AI-Questionaire\questionnaire-rag
import sys
import os

# Add the current directory (backend) to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, 'backend')

# Try both paths
sys.path.insert(0, current_dir)
sys.path.insert(0, backend_dir)

print(f"Python path: {sys.path[:2]}")

try:
    from backend.app.auth.router import router as auth_router
    print(f"✅ auth_router loaded: {type(auth_router)}")
    print(f"   Routes: {[r.path for r in auth_router.routes if hasattr(r, 'path')]}")
except Exception as e:
    print(f"❌ backend.app.auth.router failed: {e}")
    
    try:
        from app.auth.router import router as auth_router
        print(f"✅ app.auth.router loaded: {type(auth_router)}")
    except Exception as e2:
        print(f"❌ app.auth.router also failed: {e2}")

try:
    from backend.app.questionnaires.router import router as questionnaires_router
    print(f"✅ questionnaires_router loaded")
except Exception as e:
    print(f"❌ backend.app.questionnaires.router failed: {e}")
    try:
        from app.questionnaires.router import router as questionnaires_router
        print(f"✅ app.questionnaires.router loaded")
    except Exception as e2:
        print(f"❌ app.questionnaires.router also failed: {e2}")