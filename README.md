# AI Questionnaire Answering Tool (RAG-Based System)

## 1. Project Overview

Organizations frequently receive structured questionnaires such as:

* Security review questionnaires
* Vendor risk assessments
* Compliance audits
* Operational due-diligence forms

These questionnaires must be answered using internal documentation such as security policies, infrastructure documentation, and operational procedures.

Manually completing these questionnaires requires teams to search through multiple internal documents to find accurate answers and supporting evidence.

This project implements an **AI-powered Retrieval Augmented Generation (RAG) system** that automates this workflow.

The system allows users to:

1. Upload reference documents
2. Upload a structured questionnaire
3. Automatically retrieve relevant policy information
4. Generate grounded answers using an LLM
5. Attach citations from internal documentation
6. Review and edit answers before exporting the final document

The goal is to demonstrate how **AI systems can assist operational and security teams in completing structured questionnaires efficiently while ensuring answers remain grounded in verified documentation.**

---

# 2. Industry Context

### Industry

Cloud SaaS Security & Data Analytics

### Fictional Company

**DataVault Analytics**

DataVault Analytics is a fictional SaaS company that provides enterprise-grade data analytics and secure cloud storage solutions.

The platform processes sensitive enterprise data and therefore maintains strict security standards including:

* Strong authentication controls
* Encrypted data storage
* Infrastructure monitoring
* Security governance policies
* Vendor risk management procedures

To simulate a real enterprise environment, multiple internal policy documents were created to act as the **source of truth for answering questionnaires.**

---

# 3. Reference Documents

The system uses several internal policy documents that define the company’s security and operational practices.

These documents serve as the **knowledge base used by the RAG system**.

### Access Control Policy

Defines how system access is managed, including least privilege principles, identity verification, and multi-factor authentication requirements. 

### Information Security Policy

Establishes encryption standards, authentication requirements, logging procedures, and security policy governance. 

### Infrastructure Security Policy

Describes the cloud architecture, network security rules, monitoring systems, and infrastructure patch management processes. 

### Data Handling and Retention Policy

Defines how customer data is stored, classified, retained, and protected within the organization. 

### Backup and Disaster Recovery Policy

Specifies backup schedules, disaster recovery procedures, and system recovery objectives. 

### Incident Response Plan

Outlines the organization’s process for detecting, containing, investigating, and resolving security incidents. 

### Security Governance Policy

Defines the structure of the security team, governance procedures, and security responsibilities across the organization. 

### Vendor Risk Management Policy

Describes how third-party vendors are evaluated, monitored, and assessed for security risks. 

Together, these documents simulate a **real enterprise security documentation environment.**

---

# 4. Problem Statement

Enterprise customers and partners often require vendors to complete security questionnaires before approving partnerships.

These questionnaires typically ask questions such as:

* How is customer data encrypted?
* What authentication mechanisms are used?
* How are security incidents handled?
* What backup procedures exist?
* How are vendors evaluated?

Manually answering these questionnaires involves:

* Reading through many internal policy documents
* Identifying relevant sections
* Writing consistent responses
* Providing evidence from policies

This process can take **several hours or even days**.

The goal of this system is to **automate the first draft of questionnaire responses using AI while ensuring answers remain grounded in internal documentation.**

---

# 5. System Features

## User Authentication

The application requires users to sign up and log in before accessing the system.

Authentication includes:

* Secure password hashing
* Token-based authentication
* User-specific document storage

Each user's documents and questionnaires are stored independently in the database.

---

## Upload Reference Documents

Users upload internal policy documents which serve as the knowledge base for the system.

Supported formats include:

* PDF
* DOCX
* Text files

Uploaded documents are automatically processed and prepared for retrieval.

---

## Upload Questionnaire

Users upload a questionnaire document containing multiple structured questions.

The system automatically:

1. Parses the questionnaire
2. Extracts individual questions
3. Stores them in the database
4. Processes each question independently through the RAG pipeline

---

## AI-Generated Answers

For each question:

1. The system retrieves relevant information from the reference documents
2. Retrieved content is provided as context to the LLM
3. The LLM generates an answer based only on the retrieved information

If no relevant information exists in the reference documents, the system returns:

**"Not found in references."**

This prevents hallucinated responses.

---

## Citations

Every generated answer includes at least one citation referencing the document used.

This allows reviewers to verify the source of each answer.

---

## Review and Edit

Before exporting the final questionnaire, users can:

* Review generated answers
* Edit responses manually
* Improve clarity or accuracy

This ensures human oversight remains part of the process.

---

## Export Completed Questionnaire

After review, the system generates a downloadable document where:

* Original questions remain unchanged
* Generated answers appear below each question
* Citations are included with answers

This preserves the original questionnaire structure.

---

# 6. Nice-to-Have Features Implemented

### Confidence Score

Each answer includes a confidence score indicating the strength of retrieved evidence.

### Evidence Snippets

Relevant text excerpts from reference documents are displayed to show the supporting evidence.

### Coverage Summary

A summary shows:

* Total questions
* Questions answered
* Questions marked "Not found in references"

---

# 7. System Architecture

## Backend

Framework: **FastAPI**

Responsibilities:

* API endpoints
* Authentication
* Document processing
* RAG pipeline
* Database operations

---

## Frontend

Framework: **Streamlit**

Responsibilities:

* User interface
* File uploads
* Viewing generated answers
* Editing responses
* Exporting documents

---

## Database

**SQLite**

Stores:

* Users
* Uploaded documents
* Questionnaires
* Generated answers

---

# 8. AI Pipeline

The system follows a Retrieval Augmented Generation workflow.

### Step 1 — Document Parsing

Reference documents are parsed using libraries such as:

* PyPDF2
* pdfplumber
* docx2txt

---

### Step 2 — Text Chunking

Large documents are split into smaller chunks to improve retrieval accuracy.

---

### Step 3 — Embedding Generation

Each chunk is converted into a vector embedding using a sentence transformer model.

---

### Step 4 — Similarity Search

When a question is asked:

* The question is converted into an embedding
* The system retrieves the most similar document chunks

---

### Step 5 — Context Construction

Retrieved chunks are combined into a context block.

---

### Step 6 — Answer Generation

The LLM generates an answer using only the provided context.

If the context does not contain relevant information, the system responds:

**"Not found in references."**

---

# 9. Technology Stack

Backend
FastAPI

Frontend
Streamlit

Database
SQLite

LLM
Groq API (LLaMA3)

Embedding Model
Sentence Transformers

Document Processing
PyPDF2
pdfplumber
docx2txt

Vector Retrieval
Scikit-learn similarity search

---

# 10. Assumptions

* Internal policy documents contain accurate information
* Questionnaires follow a structured format
* Answers must be grounded in reference documents

---

# 11. Trade-offs

To keep the system manageable within the assignment scope:

* A lightweight vector search approach was used instead of a dedicated vector database
* The UI focuses on functionality rather than advanced design
* Only common document formats are supported

---

# 12. Future Improvements

Possible future enhancements include:

* Improved semantic search and ranking
* Support for more document formats
* Version history for questionnaire runs
* Collaboration features for review workflows
* Enhanced UI/UX design

---

# 13. Running the Project Locally

Install dependencies:

```
pip install -r requirements.txt
```

Run the backend server:

```
uvicorn backend.app.main:app --reload
```

Run the frontend application:

```
streamlit run frontend/app.py
```

---

# 14. Live Demo

Live Application
(Render deployment link)

---

# 15. Repository

GitHub Repository
(https://github.com/Y-Venkata-Pavan-Kumar/questionnaire-rag)

---
