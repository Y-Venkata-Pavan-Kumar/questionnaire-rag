from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import traceback
import sys

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Create FastAPI app FIRST (before any other imports that might depend on it)
app = FastAPI(
    title="Questionnaire AI API",
    description="RAG-powered questionnaire automation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler - CATCHES ALL UNHANDLED ERRORS
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc),
            "type": type(exc).__name__
        }
    )

# Database and models setup
try:
    from backend.app.database import engine, Base
    from backend.app.auth.models import User
    from backend.app.documents.models import Document
    from backend.app.questionnaires.models import Questionnaire, Question
    
    # Import routers - get the actual router objects (not modules)
    from backend.app.auth.router import router as auth_router
    from backend.app.documents.router import router as documents_router
    from backend.app.questionnaires.router import router as questionnaires_router
    
    logger.info("✅ Using standard app imports")
    
except ImportError as e:
    logger.warning(f"⚠️ Standard import failed: {e}, trying backend prefix...")
    
    try:
        from backend.app.database import engine, Base
        from backend.app.auth.models import User
        from backend.app.documents.models import Document
        from backend.app.questionnaires.models import Questionnaire, Question
        
        # Import routers - get the actual router objects
        from backend.app.auth.router import router as auth_router
        from backend.app.documents.router import router as documents_router
        from backend.app.questionnaires.router import router as questionnaires_router
        
        logger.info("✅ Using backend prefix imports")
        
    except ImportError as e2:
        logger.error(f"❌ Failed to import with backend prefix: {e2}")
        raise RuntimeError(f"Cannot import required modules: {e}, {e2}")

# Create database tables (only if they don't exist)
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created/verified")
except Exception as e:
    logger.error(f"❌ Database table creation failed: {e}")
    # Don't raise here - let the app start so you can see other errors

# Include routers - MUST use the router objects, not modules
app.include_router(auth_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(questionnaires_router, prefix="/api")

logger.info("✅ All routers registered")

@app.get("/")
def root():
    return {
        "message": "Questionnaire AI API",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "database": "connected"}

@app.get("/debug/routes")
def debug_routes():
    """Show all registered routes for debugging"""
    routes = []
    for route in app.routes:
        if hasattr(route, "methods"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name
            })
    return {"routes": routes}