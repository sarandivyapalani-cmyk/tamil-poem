import streamlit as st
import requests
from gtts import gTTS
import tempfile
import speech_recognition as sr
import re

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

text_input = st.text_area("உரை உள்ளிடவும்:", height=250)

# ---------------- VOICE INPUT ---------------- #

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

# ==========================================================
# 🔷 MAIN ALGORITHM: Tamil Context-Aware Adaptive System
# ==========================================================

def tamil_context_adaptive_algorithm(text, mode):

    # Step 1: Text Normalization
    clean_text = text.strip()
    clean_text = re.sub(r'\s+', ' ', clean_text)

    # Step 2: Feature Extraction
    words = clean_text.split()
    long_words = [w for w in words if len(w) > 12]
    sentences = re.split(r'[.!?]', clean_text)
    sentences = [s for s in sentences if s.strip() != ""]

    word_count = len(words)
    sentence_count = len(sentences)
    long_word_count = len(long_words)

    # Step 3: Complexity Score Calculation
    if sentence_count == 0:
        avg_sentence_length = word_count
    else:
        avg_sentence_length = word_count / sentence_count

    complexity_score = (
        (avg_sentence_length * 0.5) +
        (long_word_count * 0.3) +
        (word_count * 0.2)
    )

    # Step 4: Adaptive Temperature Selection
    if not mode.startswith("Phase 1"):
        temperature = 0.2
    else:
        if complexity_score > 25:
            temperature = 0.2
        elif complexity_score > 15:
            temperature = 0.3
        else:
            temperature = 0.4

    return complexity_score, temperature

# ---------------- PROMPT GENERATOR ---------------- #

def generate_prompt(text, mode):

    if mode.startswith("Phase 1"):
        return f"""
You are an experienced Tamil school teacher.

Simplify the text into clear, easy modern Tamil.
Understand meaning fully before rewriting.
Break long sentences.
Use spoken-style Tamil.
Maintain original meaning.

Text:
{text}
"""

    else:
        return f"""
நீங்கள் ஒரு தமிழ் இலக்கிய மற்றும் இலக்கண நிபுணர்.

உரை:
{text}

1. இலக்கிய விளக்கம் (ஒவ்வொரு பகுதியும் 6–7 வாக்கியங்கள்)
A) நேரடி பொருள்
B) உட்பொருள்
C) வாழ்க்கை நெறி
D) சமூக கோணம்

2. துல்லியமான இலக்கண பகுப்பாய்வு
3 அல்லது 4 சரியான சொற்கள் மட்டும்.
ஒவ்வொரு சொல்லுக்கும்:
சொல்:
அடிப்படை வடிவம்:
இலக்கண வகை:
விளக்கம்:

3. முடிவு (4–5 வாக்கியங்கள்)
"""

# ---------------- SARVAM API CALL ---------------- #

def call_sarvam(prompt, temperature):

    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }

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
        return "API Error"

    return response.json()["choices"][0]["message"]["content"]

# ---------------- PROCESS ---------------- #

if st.button("Process"):

    if text_input.strip() == "":
        st.warning("உரை உள்ளிடவும்")
    else:
        with st.spinner("Processing..."):

            # Run Main Algorithm
            complexity_score, temperature = tamil_context_adaptive_algorithm(text_input, mode)

            st.write(f"Complexity Score: {round(complexity_score,2)}")
            st.write(f"Adaptive Temperature: {temperature}")

            # Generate Prompt
            prompt = generate_prompt(text_input, mode)

            # Generate Output
            result = call_sarvam(prompt, temperature)

            st.markdown("---")
            st.markdown(result)

            # TTS only for Phase 1
            if mode.startswith("Phase 1"):
                tts = gTTS(result, lang="ta")
                temp_audio = tempfile.NamedTemporaryFile(delete=False)
                tts.save(temp_audio.name)
                st.audio(temp_audio.name)
