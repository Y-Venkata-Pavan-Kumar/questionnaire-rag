from sqlalchemy import Column, Integer, String, ForeignKey, Text, JSON, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

try:
    from backend.app.database import Base
except ImportError:
    from backend.app.database import Base

class Questionnaire(Base):
    __tablename__ = "questionnaires"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    original_file = Column(String)
    status = Column(String, default="uploaded")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    questions = relationship("Question", back_populates="questionnaire", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    questionnaire_id = Column(Integer, ForeignKey("questionnaires.id"))
    question_number = Column(Integer)
    question_text = Column(Text)
    
    generated_answer = Column(Text)
    confidence_score = Column(Integer)
    citations = Column(JSON, default=list)
    
    final_answer = Column(Text)
    edited_by_user = Column(Boolean, default=False)
    not_found_in_refs = Column(Boolean, default=False)
    
    questionnaire = relationship("Questionnaire", back_populates="questions")