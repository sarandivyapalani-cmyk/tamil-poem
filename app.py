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

st.set_page_config(page_title="AI Tamil Linguistic System", layout="wide")

st.title("AI அடிப்படையிலான தமிழ் விளக்கம் மற்றும் இலக்கண பகுப்பாய்வு")

# ---------------- MODE ---------------- #

mode = st.radio(
    "Mode தேர்வு செய்யவும்:",
    (
        "Phase 1: Any Language → Simple Tamil",
        "Phase 2: தமிழ் உரை → கல்வி & இலக்கண பகுப்பாய்வு"
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

# ---------------- VOICE INPUT (Phase 1 Only) ---------------- #

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

# ---------------- PROMPT FUNCTION ---------------- #

def generate_prompt(text, mode):

    # ---------- PHASE 1 ----------
    if mode.startswith("Phase 1"):
        return f"""
You are an experienced Tamil teacher.

Given text (any language):

{text}

STRICT RULES:

1. Understand full meaning first.
2. Do NOT translate word-by-word.
3. Rewrite fully in very simple, natural Tamil.
4. Break long sentences if needed.
5. Replace difficult words with easy Tamil.
6. Slightly explain naturally inside paragraph.
7. Do NOT retain foreign sentence structure.
8. Output must feel like human explanation.
9. Support long paragraphs properly.

Give only final simplified Tamil text.
"""

    # ---------- PHASE 2 ----------
    else:
        return f"""
நீங்கள் ஒரு அனுபவமுள்ள தமிழ் ஆசிரியர் மற்றும் இலக்கண நிபுணர்.

கொடுக்கப்பட்ட உரை:

{text}

---------------------------------------
INTERNAL PROCESS (Do not display):
1. ஒவ்வொரு சொல்லையும் பிரித்து ஆராயவும்.
2. சொல்லின் அடிப்படை வடிவத்தை கண்டறியவும்.
3. இலக்கண வகையை உறுதி செய்யவும்.
4. வேற்றுமை உருபு / காலம் / எண் ஆகியவை சரிபார்க்கவும்.
5. பின்னர் இறுதி பதிலை உருவாக்கவும்.
---------------------------------------

FINAL OUTPUT FORMAT:

### 1. ஆழமான விளக்கம்

- ஒரே ஒரு விரிவான, நீளமான, மனித ஆசிரியர் நடை.
- எடுத்துக்காட்டுகளுடன்.
- தேவையற்ற ஆங்கிலம் சேர்க்க வேண்டாம்.

---------------------------------------

### 2. இலக்கண அட்டவணை

கீழ்கண்ட வகைகளில் உள்ளவற்றை மட்டும் பயன்படுத்தவும்:

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

இல்லாதவற்றை குறிப்பிட வேண்டாம்.
புதிய வகைகள் உருவாக்க வேண்டாம்.

---------------------------------------

### 3. வாழ்க்கை எடுத்துக்காட்டு

---------------------------------------

### 4. சுருக்கமாக கருத்து (3-4 வரிகள்)

---------------------------------------

### 5. மாணவர்கள் கற்றுக்கொள்ளும் அம்சங்கள்

---------------------------------------

### 6. நம்பகத்தன்மை அளவு

High / Medium / Low (grammar clarity அடிப்படையில்)

---------------------------------------

ரோபோ மாதிரி பதில் தரக்கூடாது.
அறிவியல் மற்றும் இலக்கண ரீதியாக துல்லியமாக இருக்க வேண்டும்.
"""

# ---------------- API CALL ---------------- #

def call_sarvam(prompt, mode):

    temperature = 0.3 if mode.startswith("Phase 1") else 0.05

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

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Error occurred"

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

            # Voice Output only Phase 1
            if mode.startswith("Phase 1"):
                tts = gTTS(result, lang="ta")
                temp_audio = tempfile.NamedTemporaryFile(delete=False)
                tts.save(temp_audio.name)
                st.audio(temp_audio.name)
