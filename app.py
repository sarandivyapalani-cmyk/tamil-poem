import streamlit as st
import requests
from gtts import gTTS
import tempfile
import speech_recognition as sr
from PIL import Image
import pytesseract

# ----------------------------
# CONFIG
# ----------------------------

SARVAM_API_KEY = st.secrets["SARVAM_API_KEY"]
SARVAM_URL = "https://api.sarvam.ai/v1/chat/completions"

st.set_page_config(page_title="Tamil AI Linguistic System", layout="wide")

st.title("AI அடிப்படையிலான தமிழ் எளிமைப்படுத்தல் மற்றும் கல்வி பகுப்பாய்வு அமைப்பு")

# ----------------------------
# MODE SELECTION
# ----------------------------

mode = st.radio(
    "Mode தேர்வு செய்யவும்:",
    (
        "Phase 1: Any Language → Simple Tamil",
        "Phase 2: தமிழ் உரை → கல்வி பகுப்பாய்வு"
    )
)

st.markdown("---")

# ----------------------------
# FILE UPLOAD
# ----------------------------

uploaded_file = st.file_uploader("Text / Image Upload (Optional)", type=["txt", "png", "jpg", "jpeg"])

text_from_file = ""

if uploaded_file is not None:
    if uploaded_file.type.startswith("image"):
        image = Image.open(uploaded_file)
        text_from_file = pytesseract.image_to_string(image, lang="tam")
        st.success("படத்திலிருந்து உரை பெறப்பட்டது")
    else:
        text_from_file = uploaded_file.read().decode("utf-8")

# ----------------------------
# TEXT INPUT
# ----------------------------

text_input = st.text_area("உரை உள்ளிடவும்:", value=text_from_file, height=250)

# ----------------------------
# VOICE INPUT (PHASE 1 ONLY)
# ----------------------------

if mode.startswith("Phase 1"):
    audio_file = st.file_uploader("Voice Upload (Optional - wav/mp3)", type=["wav", "mp3"])

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

    # ------------------ PHASE 1 ------------------
    if mode.startswith("Phase 1"):
        return f"""
You are an experienced Tamil teacher.

Given the following text (may be any language):

{text}

This is NOT literal translation.

Follow strictly:

1. Understand full context first.
2. Rewrite completely in very simple, natural Tamil.
3. Break long sentences if needed.
4. Replace difficult words with easy Tamil.
5. Slightly explain meaning naturally inside paragraph.
6. Do NOT translate word-by-word.
7. Do NOT keep foreign sentence structure.
8. Output should feel like human explanation.

Give only the final simplified Tamil text.
"""

    # ------------------ PHASE 2 ------------------
    else:
        return f"""
நீங்கள் ஒரு அனுபவமுள்ள தமிழ் ஆசிரியர் மற்றும் இலக்கண நிபுணர்.

கொடுக்கப்பட்ட உரை:

{text}

கண்டிப்பாக பின்வரும் அமைப்பில் விளக்க வேண்டும்:

----------------------------------------

### 1. ஆழமான விளக்கம்

- ஒரே ஒரு விரிவான, நீளமான, இயல்பான மனித ஆசிரியர் நடைமுறை விளக்கம்.
- மாணவர்கள் புரிந்து கொள்ளும் வகையில்.
- எடுத்துக்காட்டுகளுடன்.
- தேவையற்ற ஆங்கிலம் சேர்க்க வேண்டாம்.

----------------------------------------

### 2. இலக்கண அட்டவணை

அந்த உரையில் வரும் இலக்கண கூறுகளை மட்டும் சேர்க்கவும்:

- பெயர்ச்சொல்
- வினைச்சொல்
- உரிச்சொல்
- பெயரடை
- சுட்டுப்பெயர்
- இடைச்சொல்
- வேற்றுமை உருபு
- காலம்
- எண்
- எழுத்தியல்
- சொறியல்
- பொருளியல்
- யாப்பியல் (இருந்தால் மட்டும்)

அட்டவணை வடிவம்:

சொல் | இலக்கண வகை | விளக்கம்

இல்லாதவற்றை குறிப்பிட வேண்டாம்.

----------------------------------------

### 3. எடுத்துக்காட்டு

இந்த கருத்தை புரிந்து கொள்ள வாழ்க்கை சம்பந்தப்பட்ட எடுத்துக்காட்டு தர வேண்டும்.

----------------------------------------

### 4. சுருக்கமாக கருத்து

3 முதல் 4 வரிகளில் முக்கிய கருத்து.

----------------------------------------

### 5. மாணவர்கள் அறிந்து கொள்வது

புள்ளிவிவரமாக மாணவர்கள் கற்றுக்கொள்ளும் அம்சங்களை தரவும்.

----------------------------------------

வெளியீடு தெளிவான தலைப்புகளுடன் இருக்க வேண்டும்.
ரோபோ மாதிரி பதில் தரக்கூடாது.
"""

# ----------------------------
# API CALL
# ----------------------------

def call_sarvam(prompt, mode):

    temperature = 0.3 if mode.startswith("Phase 1") else 0.15

    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "sarvam-m",
        "messages": [
            {"role": "system", "content": "You are a Tamil language expert."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": 1500
    }

    response = requests.post(SARVAM_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Error occurred"

# ----------------------------
# PROCESS BUTTON
# ----------------------------

if st.button("Process"):

    if text_input.strip() == "":
        st.warning("உரை உள்ளிடவும்")
    else:
        with st.spinner("Processing..."):
            prompt = generate_prompt(text_input, mode)
            result = call_sarvam(prompt, mode)

            st.markdown("---")
            st.markdown(result)

            # Voice Output only for Phase 1
            if mode.startswith("Phase 1"):
                tts = gTTS(result, lang="ta")
                temp_audio = tempfile.NamedTemporaryFile(delete=False)
                tts.save(temp_audio.name)
                st.audio(temp_audio.name)
