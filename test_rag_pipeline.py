import os
from sentence_transformers import SentenceTransformer
import numpy as np
import groq

# -----------------------------
# CONFIG
# -----------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise Exception("GROQ_API_KEY not set")

print("✅ GROQ API KEY FOUND")

# -----------------------------
# INIT MODELS
# -----------------------------

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

client = groq.Groq(api_key=GROQ_API_KEY)

print("✅ Embedding model loaded")
print("✅ Groq client initialized")

# -----------------------------
# MOCK DOCUMENTS
# -----------------------------

documents = [
    {
        "text": "Our SaaS platform supports Single Sign-On (SSO) using SAML 2.0 and OAuth.",
        "source": "security_policy.txt"
    },
    {
        "text": "All customer data is encrypted at rest using AES-256 encryption.",
        "source": "data_security.txt"
    },
    {
        "text": "User authentication requires multi-factor authentication (MFA).",
        "source": "authentication_policy.txt"
    }
]

print(f"📚 Loaded {len(documents)} test documents")

# -----------------------------
# CREATE EMBEDDINGS
# -----------------------------

texts = [d["text"] for d in documents]

embeddings = embed_model.encode(texts)

print("✅ Document embeddings created")

# -----------------------------
# ASK QUESTION
# -----------------------------

question = "Do you support SSO?"

print(f"\n❓ Question: {question}")

question_embedding = embed_model.encode([question])[0]

# -----------------------------
# VECTOR SEARCH
# -----------------------------

similarities = np.dot(embeddings, question_embedding)

top_index = np.argmax(similarities)

context = documents[top_index]["text"]

print("\n🔎 Retrieved context:")
print(context)

# -----------------------------
# CALL LLM
# -----------------------------

prompt = f"""
Use ONLY this context to answer the question.

Context:
{context}

Question:
{question}

If answer not present respond exactly:
Not found in references.
"""

print("\n🚀 Calling Groq LLM...")

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": "Answer security questionnaires."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.1,
    max_tokens=200
)

answer = response.choices[0].message.content

print("\n✅ LLM RESPONSE:")
print(answer)

print("\n🎯 RAG TEST SUCCESSFUL")