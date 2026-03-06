from backend.app.documents.processor import DocumentProcessor

text = DocumentProcessor.extract_text("C:/Users/yvpaw/OneDrive/Desktop/gtm/New_folder/access_control_policy.pdf")
print(len(text))
print(text[:500])