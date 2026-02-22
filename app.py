import streamlit as st
import requests
from PIL import Image
import pytesseract

# ----------------------------
# CONFIG
# ----------------------------

SARVAM_API_KEY = st.secrets["SARVAM_API_KEY"]
SARVAM_URL = "https://api.sarvam.ai/v1/chat/completions"

st.set_page_config(page_title="Tamil Linguistic System", layout="wide")

st.title("AI அடிப்படையிலான தமிழ் விளக்கம் மற்றும் இலக்கண பகுப்பாய்வு")

# ----------------------------
# PHASE SELECT
# ----------------------------

mode = st.radio(
    "Mode தேர்வு செய்யவும்:",
    (
        "Phase 1: Any Language → ஆழமான தமிழ் விளக்கம்",
        "Phase 2: தமிழ் உரை → ஆழமான பகுப்பாய்வு"
    )
)

# ----------------------------
# FILE UPLOAD
# ----------------------------

uploaded_file = st.file_uploader("கோப்பு பதிவேற்றம் (Text / Image)", type=["txt", "png", "jpg", "jpeg"])

text_from_file = ""

if uploaded_file is not None:
    if uploaded_file.type.startswith("image"):
        image = Image.open(uploaded_file)
        text_from_file = pytesseract.image_to_string(image, lang="tam")
        st.success("படத்திலிருந்து உரை பெறப்பட்டது")
    else:
        text_from_file = uploaded_file.read().decode("utf-8")

user_input = st.text_area("அல்லது உரையை இங்கே உள்ளிடவும்:", value=text_from_file, height=250)

# ----------------------------
# PROMPT
# ----------------------------

def generate_prompt(text, mode):

    if mode.startswith("Phase 1"):
        return f"""
நீங்கள் ஒரு அனுபவமுள்ள தமிழ் ஆசிரியர் போல விளக்க வேண்டும்.

கொடுக்கப்பட்ட உரை:

{text}

1. முதலில் அதை தமிழில் மாற்றவும் (தேவைப்பட்டால்).
2. ஒரே ஒரு ஆழமான, விரிவான, நீளமான விளக்கம் தர வேண்டும்.
3. மனிதர் கற்பிப்பது போல இயல்பான நடைமுறையில் எழுதவும்.
4. மறுபடியும் எளிமைப்படுத்தல் செய்ய வேண்டாம்.
5. இலக்கண கூறுகள் இருப்பின் அவற்றை அட்டவணை வடிவில் மட்டும் காட்டவும்.
6. Word Evaluation Table தரவும்.

வெளியீடு வடிவம்:

### 1. ஆழமான விளக்கம்

### 2. இலக்கண அட்டவணை
(அந்த உரையில் வரும் இலக்கண கூறுகள் மட்டும்)

Column:
சொல் | இலக்கண வகை | விளக்கம்

### 3. Word Evaluation Table
தமிழ் சொல் | அடிப்படை வடிவம் | எளிய தமிழ் | English Meaning
"""

    else:
        return f"""
நீங்கள் தமிழ் இலக்கண நிபுணர்.

கொடுக்கப்பட்ட உரை:

{text}

1. ஒரே ஒரு ஆழமான, விரிவான, நீளமான விளக்கம் தர வேண்டும்.
2. மனித ஆசிரியர் போல இயல்பான தமிழில் எழுத வேண்டும்.
3. தேவையற்ற சுருக்கம் செய்ய வேண்டாம்.
4. அந்த உரையில் வரும் இலக்கண கூறுகளை மட்டும் கண்டறியவும்:
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

5. இல்லாதவற்றை குறிப்பிட வேண்டாம்.
6. இலக்கணத்தை அட்டவணை வடிவில் மட்டும் தர வேண்டும்.
7. Word Evaluation Table தர வேண்டும்.
8. தேவையற்ற ஆங்கில விளக்கம் தர வேண்டாம்.

வெளியீடு வடிவம்:

### 1. ஆழமான விளக்கம்

### 2. இலக்கண அட்டவணை
சொல் | இலக்கண வகை | விளக்கம்

### 3. Word Evaluation Table
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
            {"role": "system", "content": "You are a Tamil linguistic expert."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }

    response = requests.post(SARVAM_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return response.text

# ----------------------------
# RUN
# ----------------------------

if st.button("பகுப்பாய்வு செய்யவும்"):

    if user_input.strip() == "":
        st.warning("உரை உள்ளிடவும்")
    else:
        with st.spinner("ஆழமான விளக்கம் உருவாக்கப்படுகிறது..."):
            prompt = generate_prompt(user_input, mode)
            result = call_sarvam(prompt)
            st.markdown("---")
            st.markdown(result)

