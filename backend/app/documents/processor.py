import PyPDF2
import docx2txt
import pandas as pd
from typing import List, Dict
import os
import re

class DocumentProcessor:
    SUPPORTED_TYPES = {'.pdf', '.docx', '.txt', '.xlsx', '.xls'}
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return DocumentProcessor._extract_pdf(file_path)
        elif ext == '.docx':
            return docx2txt.process(file_path)
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext in ['.xlsx', '.xls']:
            return DocumentProcessor._extract_excel(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    @staticmethod
    def _extract_pdf(file_path: str) -> str:
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        return text
    
    @staticmethod
    def _extract_excel(file_path: str) -> str:
        df = pd.read_excel(file_path)
        return df.to_string(index=False)
    
    @staticmethod
    def extract_questions(file_path: str) -> List[Dict]:
        """Extract numbered questions from questionnaire file."""
        text = DocumentProcessor.extract_text(file_path)
        questions = []
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Match patterns: "1.", "Q1:", "Question 1:", "1)"
            match = re.match(r'^(?:Q|Question)?\s*(\d+)[:.)]\s*(.+)', line, re.IGNORECASE)
            if match:
                q_num = int(match.group(1))
                q_text = match.group(2).strip()
                questions.append({
                    "question_number": q_num,
                    "question_text": q_text
                })
        
        # Fallback: if no structured questions found, treat paragraphs as questions
        if not questions:
            paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]
            for i, para in enumerate(paragraphs, 1):
                questions.append({
                    "question_number": i,
                    "question_text": para
                })
        
        # Sort by question number
        questions.sort(key=lambda x: x["question_number"])
        return questions