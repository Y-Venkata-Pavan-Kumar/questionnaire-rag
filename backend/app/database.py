from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

try:
    from app.config import settings
except ImportError:
    from backend.app.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Required for SQLite
)

# Session factory - creates database connections
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models (tables) - use extend_existing to avoid conflicts
class CustomBase:
    pass

Base = declarative_base(cls=CustomBase)

# Dependency - provides database session to routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()