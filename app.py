import streamlit as st
import requests
from gtts import gTTS
import tempfile
import speech_recognition as sr
from PIL import Image
import pytesseract

# ---------------- CONFIG ---------------- #

SARVAM_API_KEY = st.secrets["SARVAM_API_KEY"]
SARVAM_URL = "https://api.sarvam.ai/v1/chat/completions"

st.set_page_config(page_title="AI Tamil Scholarly Linguistic System", layout="wide")

st.title("AI அடிப்படையிலான தமிழ் விளக்கம், எளிமைப்படுத்தல் மற்றும் இலக்கிய பகுப்பாய்வு")

# ---------------- MODE ---------------- #

mode = st.radio(
    "Mode தேர்வு செய்யவும்:",
    (
        "Phase 1: Any Language → Simple Tamil",
        "Phase 2: தமிழ் உரை → Scholarly Literary & Grammar Analysis"
    )
)

st.markdown("---")

# ---------------- FILE UPLOAD ---------------- #

uploaded_file = st.file_uploader("Text / Image Upload (Optional)", type=["txt", "png", "jpg", "jpeg"])

text_from_file = ""

if uploaded_file:
    if uploaded_file.type.startswith("image"):
        image = Image.open(uploaded_file)
        text_from_file = pytesseract.image_to_string(image, lang="tam")
        st.success("படத்திலிருந்து உரை பெறப்பட்டது")
    else:
        text_from_file = uploaded_file.read().decode("utf-8")

# ---------------- TEXT INPUT ---------------- #

text_input = st.text_area("உரை உள்ளிடவும்:", value=text_from_file, height=250)

# ---------------- VOICE INPUT (PHASE 1 ONLY) ---------------- #

if mode.startswith("Phase 1"):
    audio_file = st.file_uploader("Voice Upload (wav/mp3)", type=["wav", "mp3"])
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

    # -------- PHASE 1 -------- #
    if mode.startswith("Phase 1"):
        return f"""
You are an experienced Tamil teacher.

Given text (may be any language):

{text}

STRICT RULES:

1. Understand full context first.
2. Do NOT translate word-by-word.
3. Rewrite fully in very simple, natural Tamil.
4. Break long sentences if necessary.
5. Replace difficult vocabulary with easy Tamil words.
6. Slightly clarify meaning naturally within the paragraph.
7. Do NOT retain foreign sentence structure.
8. Output must feel like human explanation.
9. Support long paragraphs clearly.

Give only final simplified Tamil text.
"""

    # -------- PHASE 2 SCHOLARLY MODE -------- #
    else:
        return f"""
நீங்கள் ஒரு தமிழ் பேராசிரியர், இலக்கிய ஆய்வாளர் மற்றும் இலக்கண நிபுணர்.

கொடுக்கப்பட்ட உரை:

{text}

-------------------------------------------------------
INTERNAL ANALYSIS (காண்பிக்க வேண்டாம்):
1. உரையின் மொத்த கருத்தை ஆய்வு செய்யவும்.
2. வெளிப்படையான பொருள் மற்றும் உட்பொருள் பிரிக்கவும்.
3. இலக்கிய, தத்துவ, சமூக கோணங்களில் அணுகவும்.
4. இலக்கண அமைப்பை சரிபார்க்கவும்.
5. பின்னர் கட்டமைக்கப்பட்ட பதிலை உருவாக்கவும்.
-------------------------------------------------------

FINAL OUTPUT FORMAT:

### 1. இலக்கிய மற்றும் தத்துவ ரீதியான ஆழமான விளக்கம்

- முதலில் நேரடி பொருள் விளக்கம்.
- பின்னர் உட்பொருள் விளக்கம்.
- ஆசிரியர்/கவிஞர் எடுத்துரைக்கும் வாழ்க்கை நெறி.
- மனித மனவியல் மற்றும் சமூக கோணத்தில் பகுப்பாய்வு.
- தமிழ் இலக்கிய பாரம்பரியத்துடன் தொடர்பு (சுருக்கமாக).
- குறைந்தது 15 வரிகள்.
- ஆய்வுத் தன்மை மற்றும் கல்வியியல் நடை.

-------------------------------------------------------

### 2. இலக்கண பகுப்பாய்வு அட்டவணை

பின்வரும் வகைகளை மட்டும் பயன்படுத்தவும்:

பெயர்ச்சொல்  
வினைச்சொல்  
உரிச்சொல்  
பெயரடை  
சுட்டுப்பெயர்  
இடைச்சொல்  
வேற்றுமை உருபு  
காலம்  
எண்  
எழுத்தியல்  
சொறியல்  
பொருளியல்  
யாப்பியல்  

அட்டவணை வடிவம்:

சொல் | இலக்கண வகை | விளக்கம்

புதிய வகைகள் உருவாக்க வேண்டாம்.
இல்லாதவற்றை சேர்க்க வேண்டாம்.

-------------------------------------------------------

### 3. கருத்து விரிவு

இன்றைய வாழ்க்கையில் இந்த கருத்து எவ்வாறு பொருந்துகிறது (5–6 வரிகள்).

-------------------------------------------------------

### 4. சுருக்கமான முடிவு

3–4 வரிகளில் மைய கருத்து.

-------------------------------------------------------

### 5. கற்றல் பயன்

மாணவர்கள் பெறும் அறிவு அம்சங்கள் (புள்ளிவிவரம்).

-------------------------------------------------------

### 6. நம்பகத்தன்மை அளவு

High / Medium / Low  
(இலக்கண தெளிவு அடிப்படையில் குறிப்பிடவும்)

-------------------------------------------------------

முக்கியம்:
- விளக்கம் ஆய்வுத் தரத்தில் இருக்க வேண்டும்.
- ரோபோ மாதிரி பதில் தரக்கூடாது.
- இலக்கண பகுதி தனியாக இருக்க வேண்டும்.
"""

# ---------------- SARVAM API CALL ---------------- #

def call_sarvam(prompt, mode):

    temperature = 0.3 if mode.startswith("Phase 1") else 0.05

    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "sarvam-m",
        "messages": [
            {"role": "system", "content": "You are a Tamil linguistic and literary expert."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": 2200
    }

    response = requests.post(SARVAM_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Error occurred"

# ---------------- PROCESS BUTTON ---------------- #

if st.button("Process"):

    if text_input.strip() == "":
        st.warning("உரை உள்ளிடவும்")
    else:
        with st.spinner("Processing..."):
            prompt = generate_prompt(text_input, mode)
            result = call_sarvam(prompt, mode)

            st.markdown("---")
            st.markdown(result)

            # Voice output only for Phase 1
            if mode.startswith("Phase 1"):
                tts = gTTS(result, lang="ta")
                temp_audio = tempfile.NamedTemporaryFile(delete=False)
                tts.save(temp_audio.name)
                st.audio(temp_audio.name)
