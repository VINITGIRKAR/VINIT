import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(input)
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def create_prompt(resume_text, job_description):
    return f"""
    Act like a skilled ATS with expertise in tech fields.
    Evaluate the resume against the JD.
    
    Resume: {resume_text}
    JD: {job_description}

    Return a JSON with this structure:
    {{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
    """

# --- Authentication ---

# Load credentials
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Streamlit App Setup
st.set_page_config(page_title="Smart ATS", page_icon="🧠", layout="centered")

# Login page
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.success(f"Welcome {name} 👋")
    
    # --- Smart ATS Frontend ---
    with st.container():
        st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Smart ATS 🧠</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size:18px;'>Boost your chances! Match your resume with job descriptions.</p>", unsafe_allow_html=True)
        st.write("---")

        jd = st.text_area("📄 Paste the Job Description Here:", height=200, placeholder="Enter the JD...")
        uploaded_file = st.file_uploader("📎 Upload Your Resume (PDF only)", type="pdf", help="Please upload a PDF format resume.")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit = st.button("🚀 Analyze My Resume", use_container_width=True)

        if submit:
            if uploaded_file is not None and jd:
                with st.spinner('Analyzing your resume... Please wait ⏳'):
                    resume_text = input_pdf_text(uploaded_file)
                    prompt = create_prompt(resume_text, jd)
                    response = get_gemini_response(prompt)
                    
                    try:
                        result = json.loads(response)
                        st.success("✅ Analysis Complete!")
                        st.subheader("📊 Match Results")
                        st.metric(label="JD Match (%)", value=result.get("JD Match", "N/A"))
                        
                        st.subheader("🧩 Missing Keywords")
                        missing_keywords = result.get("MissingKeywords", [])
                        if missing_keywords:
                            st.write(", ".join(missing_keywords))
                        else:
                            st.write("No missing keywords! Great job 👏")
                        
                        st.subheader("🧠 Profile Summary")
                        st.write(result.get("Profile Summary", "No summary provided."))
                    except:
                        st.warning("⚠️ Couldn't parse the response properly. Showing raw output:")
                        st.write(response)
            else:
                st.warning("⚠️ Please upload a resume and paste the job description.")
    
    st.write("---")
    st.markdown("<p style='text-align: center; font-size:14px;'>Made with ❤️ using Streamlit and Gemini 1.5</p>", unsafe_allow_html=True)

elif authentication_status is False:
    st.error("❌ Incorrect Username or Password")
elif authentication_status is None:
    st.warning("👤 Please enter your username and password.")

