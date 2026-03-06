from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

try:
    from app.database import Base
except ImportError:
    from backend.app.database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}  # ADD THIS LINE
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    company_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)