import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
import docx
from dotenv import load_dotenv
import json
import time

# Load environment variables
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(input)
    return response.text

def extract_text(uploaded_file):
    if uploaded_file.name.endswith('.pdf'):
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    elif uploaded_file.name.endswith('.docx'):
        doc = docx.Document(uploaded_file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    else:
        return None

def create_prompt(resume_text, job_description):
    return f"""
    Hey Act Like a skilled or very experienced ATS (Application Tracking System)
    with a deep understanding of tech field, software engineering, data science, data analyst,
    and big data engineer. Your task is to evaluate the resume based on the given job description.
    You must consider the job market is very competitive and you should provide 
    best assistance for improving the resumes. Assign the percentage matching based 
    on JD and the missing keywords with high accuracy.
    
    resume: {resume_text}
    description: {job_description}

    I want the response in one single string having the structure
    {{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
    """

# Streamlit App
st.set_page_config(page_title="Smart ATS", page_icon="🧠", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #e0f7fa, #e1bee7);
        font-family: 'Poppins', sans-serif;
    }
    h1 {
        font-size: 3rem;
        color: #4CAF50;
        text-align: center;
    }
    .subtitle {
        text-align: center;
        font-size: 20px;
        color: #555;
        margin-bottom: 20px;
    }
    div.stButton > button {
        background: linear-gradient(to right, #4CAF50, #81C784);
        color: white;
        height: 50px;
        width: 100%;
        border-radius: 10px;
        font-size: 18px;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background: linear-gradient(to right, #388E3C, #66BB6A);
        transform: scale(1.05);
    }
    .card {
        background: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        animation: fadeIn 1s ease-in-out;
        margin-bottom: 20px;
    }
    @keyframes fadeIn {
        0% {opacity: 0;}
        100% {opacity: 1;}
    }
    .footer {
        text-align: center;
        font-size: 14px;
        margin-top: 50px;
        color: #777;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1>Smart ATS 🧠</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Boost your chances! Match your resume with job descriptions.</p>", unsafe_allow_html=True)
st.write("---")

# Session State
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
    st.session_state.result_data = {}

# Tabs
tab1, tab2 = st.tabs(["📥 Upload & Input", "📊 Results"])

with tab1:
    st.header("📄 Paste Job Description & Upload Resume")
    jd = st.text_area("Job Description", height=200, placeholder="Paste the Job Description here...")
    uploaded_file = st.file_uploader(
        "Upload Resume (PDF or DOCX)", 
        type=["pdf", "docx"], 
        help="Only PDF or DOCX files are supported."
    )

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        submit = st.button("🚀 Analyze Resume", use_container_width=True)

    if submit:
        if uploaded_file is not None and jd:
            with st.spinner("Analyzing your resume... Please wait ⏳"):
                resume_text = extract_text(uploaded_file)
                if resume_text is None:
                    st.error("Unsupported file format.")
                else:
                    prompt = create_prompt(resume_text, jd)
                    response = get_gemini_response(prompt)

                    try:
                        result = json.loads(response)
                        st.session_state.result_data = result
                        st.session_state.analysis_done = True
                        st.success("✅ Resume analysis completed! Go to 'Results' tab.")
                        
                        time.sleep(1)
                        st.balloons()
                        
                    except:
                        st.session_state.result_data = {"raw_response": response}
                        st.session_state.analysis_done = True
                        st.warning("⚠️ Couldn't parse the response properly. Showing raw output in Results tab.")
        else:
            st.warning("⚠️ Please upload a resume and paste the Job Description.")

with tab2:
    st.header("📊 Your Analysis Results")

    if st.session_state.analysis_done:
        result = st.session_state.result_data
        
        if "raw_response" in result:
            st.warning("⚠️ Showing raw response:")
            st.write(result["raw_response"])
        else:
            # JD Match
            match_percentage = result.get('JD Match', "0").replace('%', '')
            try:
                match_percentage = float(match_percentage)
            except:
                match_percentage = 0.0

            st.markdown(f"""
                <div class="card">
                    <h3>📈 JD Match</h3>
                    <h1 style="color:#4CAF50;">{match_percentage:.1f}%</h1>
                </div>
            """, unsafe_allow_html=True)

            st.progress(int(match_percentage))

            # Missing Keywords
            missing_keywords = result.get("MissingKeywords", [])
            st.markdown("""<div class="card"><h3>🧩 Missing Keywords</h3>""", unsafe_allow_html=True)
            if missing_keywords:
                st.write(", ".join(missing_keywords))
            else:
                st.write("No missing keywords! Excellent profile! 👏")
            st.markdown("</div>", unsafe_allow_html=True)

            # Profile Summary
            st.markdown(f"""
                <div class="card">
                    <h3>🧠 Profile Summary</h3>
                    <p>{result.get('Profile Summary', 'No summary provided.')}</p>
                </div>
            """, unsafe_allow_html=True)

            # Download Button
            st.download_button(
                label="📥 Download Analysis Report (JSON)",
                data=json.dumps(result, indent=4),
                file_name="resume_analysis_report.json",
                mime="application/json",
                use_container_width=True
            )

    else:
        st.info("📥 Please upload and analyze your resume first in the 'Upload & Input' tab.")

# Footer
st.markdown("<div class='footer'>Made with ❤️ using Streamlit and Gemini 1.5</div>", unsafe_allow_html=True)
