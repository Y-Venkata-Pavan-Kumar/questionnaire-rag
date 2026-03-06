from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from app.database import engine, Base
    from app.auth import router as auth_router
    from app.documents import router as documents_router
    from app.questionnaires import router as questionnaires_router
except ImportError:
    from backend.app.database import engine, Base
    from backend.app.auth import router as auth_router
    from backend.app.documents import router as documents_router
    from backend.app.questionnaires import router as questionnaires_router

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Questionnaire AI API",
    description="RAG-powered questionnaire automation",
    version="1.0.0"
)

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routes
app.include_router(auth_router.router, prefix="/api")
app.include_router(documents_router.router, prefix="/api")
app.include_router(questionnaires_router.router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "Questionnaire AI API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}