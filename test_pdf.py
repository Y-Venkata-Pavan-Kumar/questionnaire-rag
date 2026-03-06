import sys
sys.path.append('backend')

# Use raw string (r"...") for Windows paths
PDF_PATH = r"C:\Users\yvpaw\OneDrive\Desktop\VENDOR_SECURITY_ASSESSMENT.pdf"

try:
    from backend.app.documents.processor import DocumentProcessor
    
    print(f"Testing PDF: {PDF_PATH}")
    
    # Test PDF extraction
    text = DocumentProcessor.extract_text(PDF_PATH)
    print(f"✅ PDF extracted: {len(text)} characters")
    print(f"Preview:\n{text[:300]}...")
    
    # Test question extraction
    questions = DocumentProcessor.extract_questions(PDF_PATH)
    print(f"\n✅ Found {len(questions)} questions")
    for q in questions[:5]:
        print(f"  Q{q['question_number']}: {q['question_text'][:60]}...")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()