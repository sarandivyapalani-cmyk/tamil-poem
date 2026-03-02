import streamlit as st
import requests
from gtts import gTTS
import tempfile
import speech_recognition as sr
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os

# ---------------- CONFIG ---------------- #

SARVAM_API_KEY = st.secrets["SARVAM_API_KEY"]
SARVAM_URL = "https://api.sarvam.ai/v1/chat/completions"

st.set_page_config(page_title="AI Tamil Linguistic System", layout="wide")

st.title("AI அடிப்படையிலான தமிழ் எளிமைப்படுத்தல் மற்றும் இலக்கண பகுப்பாய்வு")

# ---------------- MODE ---------------- #

mode = st.radio(
    "Mode தேர்வு செய்யவும்:",
    (
        "Phase 1: Any Language → Simple Tamil",
        "Phase 2: தமிழ் உரை → துல்லியமான இலக்கண பகுப்பாய்வு"
    )
)

st.markdown("---")

# ---------------- TEXT INPUT ---------------- #

text_input = st.text_area("உரை உள்ளிடவும்:", height=250)

# ---------------- VOICE INPUT (Phase 1 Only) ---------------- #

if mode.startswith("Phase 1"):
    audio_file = st.file_uploader("Voice Upload (wav)", type=["wav"])
    if audio_file:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            try:
                text_input = recognizer.recognize_google(audio_data, language="ta-IN")
                st.success("Voice converted to text")
            except:
                st.error("Voice recognition failed")

# ---------------- PROMPT GENERATOR ---------------- #

def generate_prompt(text, mode):

    if mode.startswith("Phase 1"):
        return f"""
You are an experienced Tamil school teacher.

Simplify the text into very easy modern Tamil.
Break long sentences.
Avoid literary style.
Return only simplified paragraph.

Text:
{text}
"""
    else:
        return f"""
நீங்கள் ஒரு தமிழ் இலக்கிய மற்றும் இலக்கண நிபுணர்.

உரை:
{text}

### 1. இலக்கிய மற்றும் தத்துவ விளக்கம்
ஒவ்வொரு பகுதியும் 6–7 முழு வாக்கியங்களாக இருக்க வேண்டும்.

A) நேரடி பொருள்
B) உட்பொருள்
C) வாழ்க்கை நெறி
D) சமூக / மனவியல் கோணம்

### 2. துல்லியமான இலக்கண பகுப்பாய்வு
100% உறுதியான 3 அல்லது 4 சொற்களை மட்டும் தேர்வு செய்யவும்.

வடிவம்:
சொல்:
அடிப்படை வடிவம்:
இலக்கண வகை:
விளக்கம்:

### 3. சுருக்கமான முடிவு
4–5 முழு வாக்கியங்கள்.
"""

# ---------------- SARVAM CALL ---------------- #

def call_sarvam(prompt, mode):

    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }

    temperature = 0.3 if mode.startswith("Phase 1") else 0.2

    data = {
        "model": "sarvam-m",
        "messages": [
            {"role": "system", "content": "You are a Tamil linguistic expert."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": 2000
    }

    response = requests.post(SARVAM_URL, headers=headers, json=data)

    if response.status_code != 200:
        return "Error occurred while contacting API."

    return response.json()["choices"][0]["message"]["content"]

# ---------------- PDF GENERATOR ---------------- #

def create_pdf(content):

    file_path = "output.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()

    normal_style = styles["Normal"]
    elements = []

    paragraphs = content.split("\n")

    for para in paragraphs:
        elements.append(Paragraph(para, normal_style))
        elements.append(Spacer(1, 10))

    doc.build(elements)

    return file_path

# ---------------- PROCESS ---------------- #

if st.button("Process"):

    if text_input.strip() == "":
        st.warning("உரை உள்ளிடவும்")
    else:
        with st.spinner("Processing..."):
            prompt = generate_prompt(text_input, mode)
            result = call_sarvam(prompt, mode)

            st.markdown("---")
            st.markdown(result)

            # Text-to-Speech (Phase 1)
            if mode.startswith("Phase 1"):
                tts = gTTS(result, lang="ta")
                temp_audio = tempfile.NamedTemporaryFile(delete=False)
                tts.save(temp_audio.name)
                st.audio(temp_audio.name)

            # -------- PDF DOWNLOAD BUTTON -------- #
            pdf_file = create_pdf(result)

            with open(pdf_file, "rb") as f:
                st.download_button(
                    label="📥 Download as PDF",
                    data=f,
                    file_name="Tamil_Output.pdf",
                    mime="application/pdf"
                )
