import requests
import sys

API_URL = "http://localhost:8000/api"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ5dnBhd2FuMTIzNEBnbWFpbC5jb20iLCJleHAiOjE3NzI2ODc0MjN9.1oEXLja9fRnmfwry8M8U7_uvi92uTyu3JoXft1ivWCw"

headers = {"Authorization": f"Bearer {TOKEN}"}

# File paths
REF_PDF = r"C:\Users\yvpaw\OneDrive\Desktop\SECURITY POLICY DOCUMENT.pdf"
Q_PDF = r"C:\Users\yvpaw\OneDrive\Desktop\VENDOR SECURITY ASSESSMENT.pdf"

print("="*60)
print("QUESTIONNAIRE AI - FULL WORKFLOW")
print("="*60)

# 1. Upload reference document
print("\n1. Uploading reference document...")
try:
    with open(REF_PDF, "rb") as f:
        files = {"file": ("reference.pdf", f, "application/pdf")}
        data = {"doc_type": "reference"}
        r = requests.post(f"{API_URL}/documents/upload", headers=headers, files=files, data=data)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            print(f"   ✅ Reference uploaded: {r.json()['document_id']}")
        else:
            print(f"   ❌ Failed: {r.text}")
            sys.exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# 2. Upload questionnaire
print("\n2. Uploading questionnaire...")
try:
    with open(Q_PDF, "rb") as f:
        files = {"file": ("questionnaire.pdf", f, "application/pdf")}
        data = {"title": "Vendor Security Assessment Q1 2024"}
        r = requests.post(f"{API_URL}/questionnaires/upload", headers=headers, files=files, data=data)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            result = r.json()
            q_id = result['questionnaire_id']
            print(f"   ✅ Questionnaire uploaded: ID {q_id}")
            print(f"   📋 Found {result['total_questions']} questions")
        else:
            print(f"   ❌ Failed: {r.text}")
            sys.exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# 3. Process with AI
print(f"\n3. Processing questionnaire {q_id} with AI...")
print("   ⏳ This takes 10-20 seconds...")
try:
    r = requests.post(f"{API_URL}/questionnaires/{q_id}/process", headers=headers)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        result = r.json()
        print(f"   ✅ Processing complete!")
        print(f"   📊 Total: {result['total']}")
        print(f"   ✅ Answered: {result['answered']}")
        print(f"   ❓ Not found: {result['not_found']}")
    else:
        print(f"   ❌ Failed: {r.text}")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# 4. Get review data
print(f"\n4. Getting generated answers...")
try:
    r = requests.get(f"{API_URL}/questionnaires/{q_id}/review", headers=headers)
    if r.status_code == 200:
        questions = r.json()
        print(f"   ✅ Retrieved {len(questions)} questions with answers")
        print("\n" + "="*60)
        print("SAMPLE ANSWERS:")
        print("="*60)
        for q in questions[:3]:
            print(f"\nQ{q['question_number']}: {q['question_text'][:60]}...")
            ans = q.get('final_answer') or q.get('generated_answer') or "Not found"
            print(f"A: {ans[:100]}...")
            if q.get('citations'):
                print(f"📄 Source: {q['citations'][0]['document_name']} (p.{q['citations'][0]['page_number']})")
            print(f"🎯 Confidence: {q.get('confidence_score', 0)}%")
    else:
        print(f"   ❌ Failed: {r.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*60)
print("WORKFLOW COMPLETE!")
print(f"View in frontend: http://localhost:8501")
print(f"Review ID: {q_id}")
print("="*60)