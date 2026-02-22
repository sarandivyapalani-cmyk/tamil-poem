import streamlit as st
import requests
from PIL import Image
import pytesseract

# ---------------------------
# CONFIG
# ---------------------------

SARVAM_API_KEY = st.secrets["SARVAM_API_KEY"]
SARVAM_URL = "https://api.sarvam.ai/v1/chat/completions"

st.set_page_config(page_title="Tamil Deep Simplification System", layout="wide")

st.title("தமிழ் ஆழமான விளக்கம் மற்றும் இலக்கண பகுப்பாய்வு அமைப்பு")

# ---------------------------
# FILE UPLOAD
# ---------------------------

uploaded_file = st.file_uploader("கோப்பு பதிவேற்றம் (Text / Image)", type=["txt", "png", "jpg", "jpeg"])

text_from_file = ""

if uploaded_file is not None:
    if uploaded_file.type.startswith("image"):
        image = Image.open(uploaded_file)
        text_from_file = pytesseract.image_to_string(image, lang="tam")
        st.success("படத்திலிருந்து உரை பெறப்பட்டது")
    else:
        text_from_file = uploaded_file.read().decode("utf-8")

user_input = st.text_area("அல்லது உரையை இங்கே உள்ளிடவும்:", value=text_from_file, height=200)

# ---------------------------
# PROMPT
# ---------------------------

def generate_prompt(text):

    return f"""
நீங்கள் ஒரு தமிழ் ஆசிரியர் போல விளக்க வேண்டும்.

கொடுக்கப்பட்ட உரை:

{text}

பின்வரும் முறையில் விளக்கவும்:

1. மிகவும் ஆழமான எளிய தமிழ் விளக்கம் தர வேண்டும்.
2. பள்ளி மாணவர்களுக்கு கற்பிப்பது போல இயல்பான மனித நடைமுறையில் விளக்கவும்.
3. ஒவ்வொரு வரியையும் தனித்தனியாக விளக்கவும்.
4. அந்த உரையில் வரும் அனைத்து இலக்கண கூறுகளையும் கண்டறியவும்:
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
   - யாப்பியல் (இருந்தால்)

5. சொல் - இலக்கண அட்டவணை அமைக்கவும்.
6. Word Evaluation Table அமைக்கவும்:
   தமிழ் சொல் | அடிப்படை வடிவம் | எளிய தமிழ் | English Meaning

7. தமிழ் விளக்கம் முழுவதும் இயல்பான மனித விளக்கம் போல இருக்க வேண்டும்.
8. தேவையற்ற ஆங்கில விளக்கம் தரக்கூடாது.
9. தலைப்புகளுடன் தெளிவாக அமைக்கவும்.

வெளியீட்டு வடிவம்:

### 1. எளிய தமிழ் விளக்கம்

### 2. வரி வாரியான விளக்கம்

### 3. முழுமையான இலக்கண பகுப்பு

### 4. சொல் - இலக்கண அட்டவணை

### 5. Word Evaluation Table
"""

# ---------------------------
# API CALL
# ---------------------------

def call_sarvam(prompt):

    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "sarvam-m",
        "messages": [
            {"role": "system", "content": "You are a Tamil grammar expert."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.15
    }

    response = requests.post(SARVAM_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return response.text

# ---------------------------
# RUN
# ---------------------------

if st.button("ஆழமாக பகுப்பாய்வு செய்யவும்"):

    if user_input.strip() == "":
        st.warning("உரை உள்ளிடவும்")
    else:
        with st.spinner("ஆழமான பகுப்பாய்வு நடைபெறுகிறது..."):
            prompt = generate_prompt(user_input)
            result = call_sarvam(prompt)
            st.markdown("---")
            st.markdown(result)


