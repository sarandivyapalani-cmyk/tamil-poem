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

st.set_page_config(page_title="AI Tamil Scholarly System", layout="wide")

st.title("AI அடிப்படையிலான தமிழ் எளிமைப்படுத்தல் மற்றும் துல்லிய இலக்கண பகுப்பாய்வு")

# ---------------- MODE ---------------- #

mode = st.radio(
    "Mode தேர்வு செய்யவும்:",
    (
        "Phase 1: Any Language → Simple Tamil",
        "Phase 2: தமிழ் உரை → High-Accuracy Scholarly Grammar Analysis"
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

# ---------------- PROMPT GENERATOR ---------------- #

def generate_prompt(text, mode):

    if mode.startswith("Phase 1"):
        return f"""
You are an experienced Tamil teacher.

Text:
{text}

1. Understand full context.
2. Do NOT translate word-by-word.
3. Rewrite fully in very simple, natural Tamil.
4. Break long sentences.
5. Replace difficult vocabulary.
6. Keep human explanation tone.
7. Support long paragraphs.

Return only simplified Tamil.
"""

    else:
        return f"""
நீங்கள் ஒரு தமிழ் பேராசிரியர் மற்றும் இலக்கண நிபுணர்.

உரை:
{text}

-------------------------------------
### 1. இலக்கிய மற்றும் தத்துவ விளக்கம்
- நேரடி பொருள்
- உட்பொருள்
- வாழ்க்கை நெறி
- சமூக / மனவியல் கோணம்
(குறைந்தது 15 வரிகள்)

-------------------------------------
### 2. துல்லிய இலக்கண பகுப்பாய்வு

கட்டாய செயல்முறை:

1. ஒவ்வொரு சொல்லையும் அதன் அடிப்படை வடிவத்திற்கு மாற்றவும்.
2. வேற்றுமை உருபு தனியாக குறிப்பிடவும்.
3. வினைச்சொல் என்றால் காலம் + வடிவம் குறிப்பிடவும்.
4. பெயர்ச்சொல் என்றால் எண் + வேற்றுமை குறிப்பிடவும்.
5. ஊகிக்க வேண்டாம்.
6. சந்தேகம் இருந்தால் "சந்தேகம்" என்று குறிப்பிடவும்.

அட்டவணை:

சொல் | அடிப்படை வடிவம் | இலக்கண வகை | விரிவான விளக்கம்

-------------------------------------
### 3. கருத்து விரிவு
-------------------------------------
### 4. சுருக்கமான முடிவு
-------------------------------------
### 5. கற்றல் பயன்
-------------------------------------
### 6. நம்பகத்தன்மை அளவு
High / Medium / Low
"""

# ---------------- SARVAM CALL ---------------- #

def call_sarvam(prompt, mode):

    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }

    # ---- PASS 1 ---- #
    first_data = {
        "model": "sarvam-m",
        "messages": [
            {"role": "system", "content": "You are a Tamil linguistic expert."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3 if mode.startswith("Phase 1") else 0.03,
        "max_tokens": 2200
    }

    response = requests.post(SARVAM_URL, headers=headers, json=first_data)

    if response.status_code != 200:
        return "Error occurred"

    first_output = response.json()["choices"][0]["message"]["content"]

    # ---- PASS 2 (Grammar Verification Only for Phase 2) ---- #
    if mode.startswith("Phase 2"):

        verification_prompt = f"""
You are a STRICT Tamil Ilakkanam validator.

Below is generated analysis:

{first_output}

Perform error detection:

1. Check base forms.
2. Verify case markers.
3. Verify tense and verb forms.
4. Correct wrong classifications.
5. If uncertain mark as "சந்தேகம்".
6. Do NOT change literary explanation.
7. Only correct grammar table and confidence level.

Return corrected full output.
"""

        verify_data = {
            "model": "sarvam-m",
            "messages": [
                {"role": "system", "content": "You are a strict Tamil grammar validator."},
                {"role": "user", "content": verification_prompt}
            ],
            "temperature": 0.02,
            "max_tokens": 2200
        }

        verify_response = requests.post(SARVAM_URL, headers=headers, json=verify_data)

        if verify_response.status_code == 200:
            return verify_response.json()["choices"][0]["message"]["content"]

    return first_output

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

            if mode.startswith("Phase 1"):
                tts = gTTS(result, lang="ta")
                temp_audio = tempfile.NamedTemporaryFile(delete=False)
                tts.save(temp_audio.name)
                st.audio(temp_audio.name)
