import streamlit as st
import requests
from PIL import Image
import pytesseract
import io

# ---------------------------
# CONFIG
# ---------------------------

SARVAM_API_KEY = st.secrets["SARVAM_API_KEY"]
SARVAM_URL = "https://api.sarvam.ai/v1/chat/completions"

st.set_page_config(page_title="Advanced Tamil Linguistic System", layout="wide")

st.title("AI-Based Tamil Simplification & Complete Ilakkanam Analysis")

# ---------------------------
# FILE UPLOAD
# ---------------------------

uploaded_file = st.file_uploader("Upload Text File or Image", type=["txt", "png", "jpg", "jpeg"])

text_from_file = ""

if uploaded_file is not None:
    if uploaded_file.type.startswith("image"):
        image = Image.open(uploaded_file)
        text_from_file = pytesseract.image_to_string(image, lang="tam")
        st.success("Text extracted from image")
    else:
        text_from_file = uploaded_file.read().decode("utf-8")

user_input = st.text_area("Or Enter Text Manually:", value=text_from_file, height=200)

mode = st.radio(
    "Select Mode:",
    ("Phase 1: Any Language to Deep Tamil",
     "Phase 2: Full Tamil Ilakkanam Analysis")
)

# ---------------------------
# PROMPT
# ---------------------------

def generate_prompt(text, mode):

    if mode == "Phase 1: Any Language to Deep Tamil":
        return f"""
You are a Tamil school teacher explaining clearly to students.

Text:
{text}

Do the following:

1. Convert to clear, simple Tamil.
2. Explain in teacher style, not AI style.
3. Give real-life examples.
4. Break difficult words.
5. Provide Word Evolution Table including English meaning.

Output sections:

1. எளிய தமிழ் விளக்கம்
2. வரி வாரியான விளக்கம்
3. சொற்கள் - விளக்கம் அட்டவணை
4. Word Evolution Table (Tamil | Root | Simple Tamil | English Meaning)
5. நடைமுறை எடுத்துக்காட்டு
"""

    else:
        return f"""
You are a Tamil Ilakkanam expert.

Text:
{text}

Provide deep Tamil Ilakkanam analysis including:

• எழுத்தியல்
• சொறியல்
• பொருளியல்
• யாப்பியல் (if applicable)
• பெயர்ச்சொல்
• வினைச்சொல்
• உரிச்சொல்
• வேற்றுமை உருபு
• காலம்
• எண்

Give:

1. Human-style detailed explanation.
2. Line-by-line explanation.
3. Complete Ilakkanam table.
4. Word Evolution Table (Tamil | Root | Simple Tamil | English Meaning)
5. Context explanation like teaching class.

Avoid robotic AI style.
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
            {"role": "system", "content": "You are a Tamil professor."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post(SARVAM_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return response.text

# ---------------------------
# RUN
# ---------------------------

if st.button("Process Text"):

    if user_input.strip() == "":
        st.warning("Please enter text.")
    else:
        with st.spinner("Analyzing deeply..."):
            prompt = generate_prompt(user_input, mode)
            result = call_sarvam(prompt)
            st.markdown("---")
            st.markdown(result)


