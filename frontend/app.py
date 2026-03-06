import streamlit as st
import requests
import os

# API configuration
API_URL = "https://questionnaire-rag-1.onrender.com"

# Page setup
st.set_page_config(
    page_title="Questionnaire AI",
    page_icon="📋",
    layout="wide"
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
    .info-box {
        background-color: #d1ecf1;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
    }
    .confidence-high { color: #28a745; font-weight: bold; }
    .confidence-medium { color: #ffc107; font-weight: bold; }
    .confidence-low { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Restore token from URL if exists
query_params = st.query_params

if 'token' not in st.session_state:
    st.session_state.token = query_params.get("token", None)

if 'current_page' not in st.session_state:
    st.session_state.current_page = query_params.get("page", "login")
    
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

def make_request(method, endpoint, **kwargs):
    """Make API request with auth header."""
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    url = f"{API_URL}{endpoint}"
    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        return response
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Is the server running on port 8000?")
        return None

def show_login():
    """Login/Signup page."""
    st.markdown('<p class="main-header">🔐 Welcome to Questionnaire AI</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            st.subheader("Existing User? Login")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                response = make_request(
                    "POST", 
                    "/api/auth/login",
                    data={"username": email, "password": password}
                )
                if response and response.status_code == 200:
                    data = response.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.user_email = email
                    st.session_state.current_page = "dashboard"
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with tab2:
        with st.form("signup_form"):
            st.subheader("New User? Create Account")
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_pass")
            company = st.text_input("Company Name", key="signup_company")
            signup_submit = st.form_submit_button("Create Account", use_container_width=True)
            
            if signup_submit:
                response = make_request(
                    "POST",
                    "/api/auth/signup",
                    json={
                        "email": new_email,
                        "password": new_password,
                        "company_name": company
                    }
                )

                if response and response.status_code == 200:
                    st.success("Account created successfully! Please login.")
                    st.session_state.user_email = new_email
                    st.session_state.current_page = "login"
                    st.rerun()
                else:
                    if response:
                        st.error(f"Signup failed: {response.text}")
                    else:
                        st.error("Backend connection failed")
def show_dashboard():
    """Main dashboard."""
    st.markdown(f'<p class="main-header">📋 Dashboard - {st.session_state.user_email}</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("Navigation")
        if st.button("➕ New Questionnaire", use_container_width=True):
            st.session_state.current_page = "upload"
            st.query_params["page"] = "upload"
            st.rerun()
        if st.button("📚 Reference Docs", use_container_width=True):
            st.session_state.current_page = "references"
            st.query_params["page"] = "references"
            st.rerun()
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.query_params.clear()
            st.rerun()
    
    # Quick Access - Manual Review Entry
    st.subheader("Quick Access")
    manual_id = st.number_input("Enter Questionnaire ID to Review", min_value=1, value=4, step=1)
    if st.button("🔍 Go to Review", use_container_width=True):
        st.session_state.current_qid = int(manual_id)
        st.session_state.current_page = "review"

        st.query_params["page"] = "review"

        st.rerun()
    
    st.divider()
    
    # Stats
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Questionnaires", "0")
    col2.metric("Processed", "0")
    col3.metric("Pending Review", "0")
    
    st.info("👆 Use the sidebar to upload a new questionnaire")
def show_upload():
    """Upload questionnaire and reference docs."""
    st.markdown('<p class="main-header">⬆️ Upload Questionnaire</p>', unsafe_allow_html=True)
    
    with st.form("upload_form"):
        title = st.text_input("Questionnaire Title", placeholder="e.g., Q1 2024 Security Assessment")
        
        st.subheader("1. Upload Questionnaire (PDF, DOCX, or Excel)")
        q_file = st.file_uploader("Select file", type=['pdf', 'docx', 'xlsx', 'xls'], key="q_upload")
        
        st.subheader("2. Upload Reference Documents")
        st.info("These documents will be used to answer the questionnaire")
        ref_files = st.file_uploader(
            "Select reference files (multiple allowed)", 
            type=['pdf', 'docx', 'txt'], 
            accept_multiple_files=True,
            key="ref_upload"
        )
        
        # SUBMIT BUTTON - MUST BE LAST INSIDE FORM
        submitted = st.form_submit_button("Process Questionnaire", use_container_width=True)
    
    # FORM PROCESSING - OUTSIDE FORM BLOCK
    if submitted:

        # Check login session
        if not st.session_state.get("token"):
            st.error("⚠️ Session expired. Please login again.")
            return
        if not title:
            st.error("Please enter a questionnaire title")
            return
        if not q_file:
            st.error("Please upload a questionnaire file")
            return
        if not ref_files:
            st.error("Please upload at least one reference document")
            return
        
        with st.spinner("Processing... This may take a few minutes."):
            # Upload reference documents first
            for ref_file in ref_files:

                files = {"file": (ref_file.name, ref_file.getvalue())}
                data = {"doc_type": "reference"}

                ref_response = make_request(
                    "POST",
                    "/api/documents/upload",
                    files=files,
                    data=data
                )

                if not ref_response:
                    st.warning(f"⚠️ Skipped {ref_file.name} (connection error)")
                    continue

                if ref_response.status_code == 401:
                    st.error("⚠️ Session expired. Please login again.")
                    return

                if ref_response.status_code != 200:
                    st.warning(f"⚠️ Skipped {ref_file.name}")
                    continue
            
            # Upload questionnaire
            files = {"file": (q_file.name, q_file.getvalue(), q_file.type)}
            data = {"title": title}
            q_response = make_request("POST", "/api/questionnaires/upload", files=files, data=data)
            
            if q_response and q_response.status_code == 200:
                result = q_response.json()
                q_id = result["questionnaire_id"]
                
                # Process with AI
                process_response = make_request("POST", f"/api/questionnaires/{q_id}/process")
                
                if process_response and process_response.status_code == 200:
                    st.success("✅ Questionnaire processed!")
                    st.session_state.current_qid = q_id
                    st.session_state.current_page = "review"
                    st.rerun()
                else:
                    st.error("Processing failed")
            else:
                st.error("Upload failed")
def show_review():
    """Review and edit AI-generated answers."""
    q_id = st.session_state.get('current_qid')
    if not q_id:
        st.error("No questionnaire selected")
        return
    
    st.markdown('<p class="main-header">✏️ Review Answers</p>', unsafe_allow_html=True)
    
    # Fetch data
    response = make_request("GET", f"/questionnaires/{q_id}/review")
    if not response or response.status_code != 200:
        st.error("Could not load questionnaire")
        return
    
    questions = response.json()
    
    # Summary
    total = len(questions)
    answered = len([q for q in questions if not q.get('not_found_in_refs', False)])
    avg_confidence = sum([q.get('confidence_score', 0) or 0 for q in questions]) / total if total > 0 else 0
    
    with st.container():
        st.subheader("📊 Coverage Summary")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total", total)
        col2.metric("Answered", answered)
        col3.metric("Not Found", total - answered)
        col4.metric("Avg Confidence", f"{avg_confidence:.0f}%")
    
    st.divider()
    
    # Questions
    st.subheader("Questions & Answers")
    
    edited_answers = {}
    
    for idx, q in enumerate(questions):
        with st.container(border=True):
            col1, col2 = st.columns([1, 6])
            col1.markdown(f"**Q{q['question_number']}**")
            
            with col2:
                st.write(q['question_text'])
                
                # Confidence badge
                conf = q.get('confidence_score', 0) or 0
                if conf >= 80:
                    st.markdown(f'<span class="confidence-high">🟢 High Confidence ({conf}%)</span>', unsafe_allow_html=True)
                elif conf >= 60:
                    st.markdown(f'<span class="confidence-medium">🟡 Medium ({conf}%)</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="confidence-low">🔴 Low ({conf}%)</span>', unsafe_allow_html=True)
                
                # Answer editor
                current = q.get('final_answer') or q.get('generated_answer') or "Not found in references."
                
                if q.get('not_found_in_refs'):
                    st.markdown(f'<div class="error-box">⚠️ {current}</div>', unsafe_allow_html=True)
                else:
                    edited_answers[q['question_id']] = st.text_area(
                        "Edit answer if needed:",
                        value=current,
                        key=f"edit_{q['question_id']}",
                        height=100
                    )
                
                # Citations
                if q.get('citations'):
                    with st.expander("📄 View Sources"):
                        for c in q['citations']:
                            st.caption(f"• {c['document_name']} (Page {c['page_number']})")
    
    # Actions
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Changes", use_container_width=True):
            saved = 0
            for qid, answer in edited_answers.items():
                resp = make_request(
                    "POST",
                    f"/questionnaires/{q_id}/update-answer",
                    data={"question_id": qid, "final_answer": answer}
                )
                if resp and resp.status_code == 200:
                    saved += 1
            
            if saved == len(edited_answers):
                st.success(f"✅ Saved {saved} answers!")
            else:
                st.warning(f"Saved {saved}/{len(edited_answers)} answers")
    
    with col2:
        export_format = st.selectbox("Format", ["docx", "xlsx"])
        if st.button("📥 Export Document", use_container_width=True):
            with st.spinner("Generating file..."):
                resp = make_request(
                    "POST",
                    f"/questionnaires/{q_id}/export?format={export_format}"
                )
                if resp and resp.status_code == 200:
                    # Get filename from headers
                    filename = f"questionnaire_{q_id}.{export_format}"
                    st.download_button(
                        "⬇️ Download File",
                        data=resp.content,
                        file_name=filename,
                        mime="application/octet-stream"
                    )
                else:
                    st.error("Export failed")

def show_references():
    """Manage reference documents."""
    st.markdown('<p class="main-header">📚 Reference Documents</p>', unsafe_allow_html=True)
    
    # List existing
    resp = make_request("GET", "/documents/list?doc_type=reference")
    if resp and resp.status_code == 200:
        docs = resp.json()
        if docs:
            st.subheader("Uploaded Documents")
            for d in docs:
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    col1.write(f"**{d['filename']}**")
                    col1.caption(f"Uploaded: {d['upload_date']}")
        else:
            st.info("No reference documents uploaded yet")
    else:
        st.warning("Could not load document list")
def navigate(page):
    st.session_state.current_page = page
    st.query_params["page"] = page
    st.rerun()
# Page router
if st.session_state.current_page == "login":
    show_login()
elif st.session_state.current_page == "dashboard":
    show_dashboard()
elif st.session_state.current_page == "upload":
    show_upload()
elif st.session_state.current_page == "review":
    show_review()
elif st.session_state.current_page == "references":
    show_references()