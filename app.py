import streamlit as st
import requests
from gtts import gTTS
import tempfile
import speech_recognition as sr
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import re

# ---------------- CONFIG ---------------- #

SARVAM_API_KEY = st.secrets["SARVAM_API_KEY"]
SARVAM_URL = "https://api.sarvam.ai/v1/chat/completions"

SIMILARITY_THRESHOLD = 0.75

st.set_page_config(page_title="AI Tamil Linguistic System", layout="wide")

st.title("AI அடிப்படையிலான தமிழ் எளிமைப்படுத்தல் மற்றும் இலக்கண பகுப்பாய்வு")

# ---------------- LOAD EMBEDDING MODEL ---------------- #

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

embedding_model = load_embedding_model()

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

# ---------------- MORPHOLOGICAL PREPROCESSING ---------------- #

def morphological_preprocessing(text):
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    words = text.split()
    long_words = [w for w in words if len(w) > 12]

    return {
        "clean_text": text,
        "long_word_count": len(long_words),
        "word_count": len(words)
    }

# ---------------- COMPLEXITY SCORING ---------------- #

def calculate_complexity_score(text, long_word_count):
    sentences = re.split(r'[.!?]', text)
    sentences = [s for s in sentences if s.strip() != ""]

    if len(sentences) == 0:
        return 0

    avg_sentence_length = len(text.split()) / len(sentences)

    complexity_score = (
        (avg_sentence_length * 0.5) +
        (long_word_count * 0.3) +
        (len(text.split()) * 0.2)
    )

    return complexity_score

# ---------------- ADAPTIVE TEMPERATURE ---------------- #

def adaptive_temperature(score, mode):
    if not mode.startswith("Phase 1"):
        return 0.2  # Stable output for analysis mode

    if score > 25:
        return 0.2
    elif score > 15:
        return 0.3
    else:
        return 0.4

# ---------------- PROMPT GENERATOR ---------------- #

def generate_prompt(text, mode):

    if mode.startswith("Phase 1"):
        return f"""
You are an experienced Tamil school teacher.

Task:
Simplify the given text into very easy, clear, modern Tamil.

Text:
{text}

STRICT RULES:
- Do NOT translate word-by-word.
- Understand full meaning first.
- Rewrite completely in simple spoken Tamil.
- Break long sentences.
- Replace difficult vocabulary.
- Suitable for school students.
Return only simplified Tamil paragraph.
"""

    else:
        return f"""
நீங்கள் ஒரு தமிழ் இலக்கிய மற்றும் இலக்கண நிபுணர்.

உரை:
{text}

### 1. இலக்கிய விளக்கம்
A) நேரடி பொருள் (6–7 வாக்கியங்கள்)
B) உட்பொருள் (6–7 வாக்கியங்கள்)
C) வாழ்க்கை நெறி (6–7 வாக்கியங்கள்)
D) சமூக கோணம் (6–7 வாக்கியங்கள்)

### 2. துல்லியமான இலக்கண பகுப்பாய்வு
3 அல்லது 4 தெளிவான மற்றும் 100% சரியான சொற்கள் மட்டும்.
ஒவ்வொரு சொல்லுக்கும்:
சொல்:
அடிப்படை வடிவம்:
இலக்கண வகை:
விளக்கம்:

### 3. முடிவு
(4–5 முழு வாக்கியங்கள்)
"""

# ---------------- SARVAM CALL ---------------- #

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

# ---------------- SEMANTIC SIMILARITY ---------------- #

def compute_similarity(original, generated):
    embeddings = embedding_model.encode([original, generated])
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return similarity

# ---------------- PROCESS ---------------- #

if st.button("Process"):

    if text_input.strip() == "":
        st.warning("உரை உள்ளிடவும்")
    else:
        with st.spinner("Processing..."):

            # 1️⃣ Preprocessing
            morph_data = morphological_preprocessing(text_input)

            # 2️⃣ Complexity
            score = calculate_complexity_score(
                morph_data["clean_text"],
                morph_data["long_word_count"]
            )

            # 3️⃣ Adaptive Temperature
            temperature = adaptive_temperature(score, mode)

            st.write(f"Complexity Score: {round(score,2)}")
            st.write(f"Adaptive Temperature: {temperature}")

            # 4️⃣ Generate Prompt
            prompt = generate_prompt(text_input, mode)

            # 5️⃣ Generate Output
            result = call_sarvam(prompt, temperature)

            # ---------------- PHASE 1 VALIDATION ---------------- #
            if mode.startswith("Phase 1"):

                similarity = compute_similarity(text_input, result)
                st.write(f"Semantic Similarity: {round(similarity,3)}")

                if similarity < SIMILARITY_THRESHOLD:
                    st.warning("Low similarity detected. Regenerating...")
                    result = call_sarvam(prompt, temperature)
                    similarity = compute_similarity(text_input, result)
                    st.write(f"New Similarity: {round(similarity,3)}")

            else:
                st.info("Phase 2: Interpretative generation mode. Similarity validation skipped.")

            st.markdown("---")
            st.markdown(result)

            # TTS only for Phase 1
            if mode.startswith("Phase 1"):
                tts = gTTS(result, lang="ta")
                temp_audio = tempfile.NamedTemporaryFile(delete=False)
                tts.save(temp_audio.name)
                st.audio(temp_audio.name)
