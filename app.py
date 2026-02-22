import streamlit as st
import requests
from gtts import gTTS
import tempfile
import speech_recognition as sr

# ----------------------------
# CONFIG
# ----------------------------

SARVAM_API_KEY = st.secrets["SARVAM_API_KEY"]
SARVAM_URL = "https://api.sarvam.ai/v1/chat/completions"

st.set_page_config(page_title="Tamil AI Linguistic System", layout="wide")

st.title("AI அடிப்படையிலான தமிழ் எளிமைப்படுத்தல் மற்றும் கல்வி பகுப்பாய்வு அமைப்பு")

mode = st.radio(
    "Mode தேர்வு செய்யவும்:",
    (
        "Phase 1: Any Language → Simple Tamil",
        "Phase 2: தமிழ் உரை → கல்வி பகுப்பாய்வு"
    )
)

# ----------------------------
# INPUT SECTION
# ----------------------------

st.subheader("உரை உள்ளீடு")

text_input = st.text_area("Text Paste செய்யவும்:", height=200)

audio_file = st.file_uploader("Voice Upload (Optional)", type=["wav", "mp3"])

# Voice to text
if audio_file:
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            text_input = recognizer.recognize_google(audio_data, language="ta-IN")
            st.success("Voice converted to text")
        except:
            st.error("Voice recognition failed")

# ----------------------------
# PROMPT GENERATOR
# ----------------------------

def generate_prompt(text, mode):

    if mode.startswith("Phase 1"):
        return f"""
Convert the following text into very simple, natural Tamil.

Text:
{text}

Instructions:
1. Understand full context.
2. Rewrite fully in easy Tamil.
3. Suitable for common people.
4. Avoid literal translation.
5. Paragraph format.
6. Do not add grammar analysis.
"""

    else:
        return f"""
You are a Tamil school teacher.

Given Text:
{text}

Provide:

1. Very deep step-by-step explanation in Tamil.
2. Explain like teaching students.
3. No robotic AI tone.
4. Provide Ilakkanam table (only those present).
5. Provide Word Evolution Table.

Output format:

### 1. ஆழமான விளக்கம்

### 2. இலக்கண அட்டவணை
சொல் | இலக்கண வகை | விளக்கம்

### 3. Word Evolution Table
தமிழ் சொல் | அடிப்படை வடிவம் | எளிய தமிழ் | English Meaning
"""

# ----------------------------
# API CALL
# ----------------------------

def call_sarvam(prompt):

    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "sarvam-m",
        "messages": [
            {"role": "system", "content": "You are Tamil expert."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post(SARVAM_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Error occurred"

# ----------------------------
# PROCESS
# ----------------------------

if st.button("Process"):

    if text_input.strip() == "":
        st.warning("Text required")
    else:
        with st.spinner("Processing..."):
            prompt = generate_prompt(text_input, mode)
            result = call_sarvam(prompt)

            st.markdown("---")
            st.markdown(result)

            # Tamil Voice Output for Phase 1
            if mode.startswith("Phase 1"):
                tts = gTTS(result, lang="ta")
                temp_audio = tempfile.NamedTemporaryFile(delete=False)
                tts.save(temp_audio.name)
                st.audio(temp_audio.name)

