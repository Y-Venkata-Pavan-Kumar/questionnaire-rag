from typing import List, Dict
import re

class TextChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, source_doc: str) -> List[Dict]:
        """Split text into chunks with metadata."""
        chunks = []
        
        # Split by pages first (PDF markers)
        pages = re.split(r'--- Page (\d+) ---', text)
        
        if len(pages) > 1:
            for i in range(1, len(pages), 2):
                page_num = int(pages[i])
                page_text = pages[i + 1]
                page_chunks = self._chunk_page(page_text, source_doc, page_num)
                chunks.extend(page_chunks)
        else:
            chunks = self._chunk_page(text, source_doc, 1)
        
        return chunks
    
    def _chunk_page(self, text: str, source_doc: str, page_num: int) -> List[Dict]:
        """Chunk a single page by sentences."""
        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_length = len(sentence)
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    "text": chunk_text,
                    "source_doc": source_doc,
                    "page_number": page_num
                })
                
                # Start new chunk with overlap
                overlap_text = ' '.join(current_chunk[-2:]) if len(current_chunk) >= 2 else current_chunk[-1]
                current_chunk = overlap_text.split('. ') + [sentence]
                current_length = len(overlap_text) + sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # Don't forget last chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "source_doc": source_doc,
                "page_number": page_num
            })
        
        return chunks