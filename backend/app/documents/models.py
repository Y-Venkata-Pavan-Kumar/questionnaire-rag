from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

try:
    from app.database import Base
except ImportError:
    from backend.app.database import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    file_path = Column(String)
    doc_type = Column(String)
    upload_date = Column(DateTime, default=datetime.utcnow)