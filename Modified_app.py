import streamlit as st
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
    /* Main page style */
    body {
        background: linear-gradient(135deg, #e0f7fa, #e1bee7);
        font-family: 'Poppins', sans-serif;
    }
    /* Title style */
    h1 {
        font-size: 3rem;
        color: #4CAF50;
        text-align: center;
    }
    /* Subtitle */
    .subtitle {
        text-align: center;
        font-size: 20px;
        color: #555;
        margin-bottom: 20px;
    }
    /* Button style */
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
    /* Cards */
    .card {
        background: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        animation: fadeIn 1s ease-in-out;
        margin-bottom: 20px;
    }
    /* Animations */
    @keyframes fadeIn {
        0% {opacity: 0;}
        100% {opacity: 1;}
    }
    /* Footer */
    .footer {
        text-align: center;
        font-size: 14px;
        margin-top: 50px;
        color: #777;
    }
    </style>
""", unsafe_allow_html=True)

# JavaScript for auto-scroll
st.markdown("""
    <script>
    function scrollToResults() {
        const results = window.document.getElementById("results-section");
        if (results){
            results.scrollIntoView({behavior: "smooth"});
        }
    }
    </script>
""", unsafe_allow_html=True)

# Main container
with st.container():
    st.markdown("<h1>Smart ATS 🧠</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Boost your chances! Match your resume with job descriptions.</p>", unsafe_allow_html=True)
    st.write("---")

    # Input Section
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

                # Scroll to Results using JS
                st.components.v1.html("<script>scrollToResults();</script>", height=0)

                # Try parsing JSON if possible
                try:
                    result = json.loads(response)
                    st.success("✅ Analysis Complete!")

                    st.markdown("<div id='results-section'></div>", unsafe_allow_html=True)

                    # Match Result
                    st.markdown(f"""
                        <div class="card">
                            <h3>📊 JD Match</h3>
                            <h1 style="color:#4CAF50;">{result.get('JD Match', 'N/A')}%</h1>
                        </div>
                    """, unsafe_allow_html=True)

                    # Missing Keywords
                    missing_keywords = result.get("MissingKeywords", [])
                    st.markdown("""
                        <div class="card">
                            <h3>🧩 Missing Keywords</h3>
                    """, unsafe_allow_html=True)
                    if missing_keywords:
                        st.write(", ".join(missing_keywords))
                    else:
                        st.write("No missing keywords! Great job 👏")
                    st.markdown("</div>", unsafe_allow_html=True)

                    # Profile Summary
                    st.markdown(f"""
                        <div class="card">
                            <h3>🧠 Profile Summary</h3>
                            <p>{result.get('Profile Summary', 'No summary provided.')}</p>
                        </div>
                    """, unsafe_allow_html=True)

                except:
                    st.warning("⚠️ Couldn't parse the response properly. Showing raw output:")
                    st.write(response)
        else:
            st.warning("⚠️ Please upload a resume and paste the job description.")

# Footer
st.markdown("<div class='footer'>Made with ❤️ using Streamlit and Gemini 1.5</div>", unsafe_allow_html=True)
