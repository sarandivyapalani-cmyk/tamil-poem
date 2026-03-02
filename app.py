import streamlit as st
import requests
from gtts import gTTS
import tempfile
import speech_recognition as sr

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

    # -------- PHASE 1 -------- #
    if mode.startswith("Phase 1"):
        return f"""
You are an experienced Tamil school teacher.

Task:
Simplify the given text into very easy, clear, modern Tamil.

Text:
{text}

STRICT INSTRUCTIONS:

1. Do NOT translate word-by-word.
2. First understand the full meaning.
3. Rewrite the content completely in simple spoken-style Tamil.
4. Break long sentences into 2 or 3 short sentences.
5. Replace difficult vocabulary with easy everyday Tamil words.
6. If the idea is complex, explain it briefly in simple terms.
7. Maintain original meaning, but simplify structure.
8. Output must be natural and human-like.
9. Suitable for school students (age 12–16).
10. If input is already simple, improve clarity further.

Important:
- Do not copy original sentence structure.
- Do not use high literary Tamil.
- Do not add headings.
- Return only the simplified Tamil paragraph.

Now produce the simplified Tamil version.
"""

    # -------- PHASE 2 -------- #
    else:
        return f"""
நீங்கள் ஒரு தமிழ் இலக்கண நிபுணர்.

உரை:
{text}

-------------------------------------
### 1. இலக்கிய மற்றும் தத்துவ விளக்கம்
- நேரடி பொருள்
- உட்பொருள்
- வாழ்க்கை நெறி
- சமூக / மனவியல் கோணம்
(12–15 வரிகள்)

-------------------------------------
### 2. துல்லியமான இலக்கண பகுப்பாய்வு

முக்கிய வழிமுறை:

1. முழு உரையில் இருந்து இலக்கண ரீதியாக 100% உறுதியாக சரியான 3 அல்லது 4 சொற்களை மட்டும் தேர்வு செய்யவும்.
2. எந்த சந்தேகமும் உள்ள சொற்களை தேர்வு செய்யக்கூடாது.
3. வேற்றுமை குழப்பம் அல்லது கால குழப்பம் உள்ள சொற்களை தவிர்க்கவும்.
4. மிகத் தெளிவான பெயர்ச்சொல் அல்லது வினைச்சொல் வடிவங்களை மட்டும் தேர்வு செய்யவும்.
5. சந்தேகம் இருந்தால் அந்த சொல்லை முற்றிலும் தவிர்க்கவும்.

வடிவம்:

சொல்:
அடிப்படை வடிவம்:
இலக்கண வகை:
விளக்கம்:

(அட்டவணை வேண்டாம். பட்டியலாக மட்டும் தரவும்.)

-------------------------------------
### 3. சுருக்கமான முடிவு
"""

# ---------------- SARVAM CALL ---------------- #

def call_sarvam(prompt):

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
        "temperature": 0.3,
        "max_tokens": 2000
    }

    response = requests.post(SARVAM_URL, headers=headers, json=data)

    if response.status_code != 200:
        return "Error occurred"

    return response.json()["choices"][0]["message"]["content"]

# ---------------- PROCESS ---------------- #

if st.button("Process"):

    if text_input.strip() == "":
        st.warning("உரை உள்ளிடவும்")
    else:
        with st.spinner("Processing..."):
            prompt = generate_prompt(text_input, mode)
            result = call_sarvam(prompt)

            st.markdown("---")
            st.markdown(result)

            # Text-to-Speech for Phase 1
            if mode.startswith("Phase 1"):
                tts = gTTS(result, lang="ta")
                temp_audio = tempfile.NamedTemporaryFile(delete=False)
                tts.save(temp_audio.name)
                st.audio(temp_audio.name)
