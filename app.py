import streamlit as st
import google.generativeai as genai
import time

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="Appointment Companion MVP",
    page_icon="🩺",
    layout="centered"
)

# Custom CSS for a clean, professional aesthetic
st.markdown("""
    <style>
    :root {
        color-scheme: light;
    }
    .stApp {
        --primary-color: #1D4ED8;
        --background-color: #F8FAFC;
        --secondary-background-color: #FFFFFF;
        --text-color: #0F172A;
        --border-color: #E2E8F0;
        background-color: #F8FAFC;
        color: #0F172A;
    }
    .block-container {
        max-width: 860px;
        padding-top: 1.8rem;
        padding-bottom: 2rem;
        padding-left: 2.1rem;
        padding-right: 2.1rem;
        background-color: #FFFFFF;
        border: 1px solid var(--border-color);
        border-radius: 14px;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
        margin-left: auto;
        margin-right: auto;
    }
    .stMarkdown,
    .stText,
    p,
    label,
    span,
    li {
        color: #0F172A;
    }
    [data-testid="stHeading"] h1,
    [data-testid="stHeading"] h2,
    [data-testid="stHeading"] h3,
    [data-testid="stHeading"] h4 {
        color: #0F172A;
    }
    .main-header {
        color: #0F172A;
        font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
        font-weight: 650;
        text-align: center;
        margin: 0;
        font-size: 2.4rem;
        line-height: 1.2;
    }
    .sub-header {
        color: #475569;
        margin: 0.4rem 0 0.1rem 0;
        font-size: 0.98rem;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background-color: var(--primary-color);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.58rem 1rem;
        font-weight: 600;
        transition: 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #1E40AF;
        color: white;
        border: none;
    }
    [data-testid="stBaseButton-secondary"] {
        border: 1px solid var(--border-color);
        background-color: #FFFFFF;
        color: #0F172A;
    }
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div,
    .stNumberInput input,
    .stDateInput input,
    .stTimeInput input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-color: #CBD5E1 !important;
    }
    div[data-testid="stFileUploaderDropzone"] {
        background-color: #FFFFFF;
        border: 1px dashed #94A3B8;
        border-radius: 10px;
    }
    div[data-testid="stStatusWidget"] {
        background-color: #FFFFFF;
        border-radius: 10px;
        border: 1px solid var(--border-color);
    }
    div[data-testid="stAlert"] {
        border-radius: 10px;
        color: #0F172A;
    }
    div[data-testid="stExpander"] {
        background-color: white;
        border-radius: 10px;
        border: 1px solid var(--border-color);
        color: #0F172A;
    }
    [data-testid="stDivider"] {
        background-color: #CBD5E1;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API SETUP ---
# Method 1: Pulling from .streamlit/secrets.toml
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except KeyError:
    st.error("Missing API Key! Please add 'GEMINI_API_KEY' to your .streamlit/secrets.toml file.")
    st.stop()

# --- 3. UI LAYOUT ---
st.markdown("<h1 class='main-header'>🩺 Appointment Companion</h1>", unsafe_allow_html=True)
st.divider()

st.subheader("1. Upload Recording")
uploaded_file = st.file_uploader(
    "Upload a doctor visit (mp3, wav, or m4a)", 
    type=['mp3', 'wav', 'm4a'],
    help="The agent will listen to this file to extract key facts."
)

if uploaded_file:
    # Display audio player for the user
    st.audio(uploaded_file)
    
    st.subheader("2. Extraction")
    if st.button("Start Extraction Agent"):
        try:
            with st.status("Agent processing audio...", expanded=True) as status:
                st.write("Transcribing dialogue...")
                
                # We pass the bytes directly to Gemini 1.5 Flash
                # For very long files (>10MB), uploading to the File API is recommended
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                audio_content = {
                    "mime_type": f"audio/{uploaded_file.type.split('/')[-1]}",
                    "data": uploaded_file.read()
                }
                
                # The specialized "Scribe" prompt
                prompt = """
                You are a highly precise Medical Scribe Agent. 
                Listen to the provided audio of a doctor-patient encounter.
                
                Your goal is to extract the following 'Need-to-Know' facts:
                1. DIAGNOSES: Any confirmed or suspected conditions mentioned.
                2. PRESCRIPTIONS: Medication names, specific dosages, and frequency.
                3. FOLLOW-UP ORDERS: Tests, referrals, or scheduled next appointments.
                4. PATIENT INSTRUCTIONS: Key lifestyle changes or immediate next steps.

                Output the results in a clean, professional format using Markdown headers.
                If information for a category is missing, explicitly state 'None mentioned'.
                """
                
                st.write("Extracting clinical facts...")
                response = model.generate_content([prompt, audio_content])
                
                status.update(label="Extraction Complete!", state="complete", expanded=False)

            # Display Results
            st.divider()
            st.success("Analysis Ready")
            st.markdown(response.text)
            
            # Simple option to copy data
            st.download_button(
                label="Download Summary",
                data=response.text,
                file_name="visit_summary.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

else:
    st.info("Please upload an audio file to begin.")

# --- 4. FOOTER ---
st.divider()