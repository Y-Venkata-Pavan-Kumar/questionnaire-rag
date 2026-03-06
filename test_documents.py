import sys
sys.path.append('backend')

print("Testing document imports...")

try:
    from app.documents.models import Document
    print("✅ Document models imported")
    
    from app.documents.processor import DocumentProcessor
    print("✅ Document processor imported")
    
    from app.documents.chunker import TextChunker
    print("✅ Text chunker imported")
    
    from app.documents.router import router
    print("✅ Document router imported")
    
    # Test chunker
    chunker = TextChunker()
    test_chunks = chunker.chunk_text("This is page 1. This is sentence two. This is sentence three.", "test.pdf")
    print(f"✅ Chunker works: created {len(test_chunks)} chunks")
    
    print("\n" + "="*50)
    print("✅ STEP 4 COMPLETE - Document system ready!")
    print("="*50)
    
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()