import streamlit as st
import requests
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import re
import os

# ==============================
# CONFIGURATION
# ==============================

API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = st.secrets["OPENAI_API_KEY"]

MODEL_NAME = "gpt-4o-mini"  # You can change if needed
SIMILARITY_THRESHOLD = 0.75
MAX_TOKENS = 1500

# Load embedding model once
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

embedding_model = load_embedding_model()

# ==============================
# 1️⃣ MORPHOLOGICAL PREPROCESSING
# ==============================

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

# ==============================
# 2️⃣ COMPLEXITY SCORING
# ==============================

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

# ==============================
# 3️⃣ ADAPTIVE TEMPERATURE
# ==============================

def adaptive_temperature(score):
    if score > 25:
        return 0.2
    elif score > 15:
        return 0.3
    else:
        return 0.4

# ==============================
# 4️⃣ TRANSFORMER API CALL
# ==============================

def generate_explanation(text, temperature):
    prompt = f"""
You are an advanced Tamil NLP system using transformer-based contextual attention.

Your task:
- Deeply understand the meaning.
- Preserve semantic integrity.
- Simplify grammar and vocabulary.
- Expand explanation clearly.
- Provide 6 to 8 meaningful sentences in paragraph format.

Input Tamil Text:
{text}

Output:
Provide simplified Tamil explanation.
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a Tamil language expert."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": MAX_TOKENS
    }

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        st.error("API Error: " + str(response.text))
        return None

# ==============================
# 5️⃣ SEMANTIC SIMILARITY VALIDATION
# ==============================

def compute_similarity(original, generated):
    embeddings = embedding_model.encode([original, generated])
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return similarity

# ==============================
# STREAMLIT UI
# ==============================

st.set_page_config(page_title="தமிழ் விளக்க அமைப்பு", layout="wide")
st.title("📘 தமிழ் விளக்க அமைப்பு")

user_input = st.text_area("தமிழ் உரையை உள்ளிடவும்:", height=200)

if st.button("விளக்கம் உருவாக்கு"):

    if user_input.strip() == "":
        st.warning("தயவுசெய்து உரையை உள்ளிடவும்.")
    else:

        # Step 1: Preprocessing
        morph_data = morphological_preprocessing(user_input)

        # Step 2: Complexity Score
        score = calculate_complexity_score(
            morph_data["clean_text"],
            morph_data["long_word_count"]
        )

        # Step 3: Adaptive Temperature
        temp = adaptive_temperature(score)

        st.write(f"🔍 Complexity Score: {round(score,2)}")
        st.write(f"🌡 Adaptive Temperature: {temp}")

        # Step 4: Generate Explanation
        explanation = generate_explanation(user_input, temp)

        if explanation:

            # Step 5: Similarity Check
            similarity = compute_similarity(user_input, explanation)

            st.write(f"📊 Semantic Similarity: {round(similarity,3)}")

            # Regenerate if similarity too low
            if similarity < SIMILARITY_THRESHOLD:
                st.warning("Low similarity detected. Regenerating...")
                explanation = generate_explanation(user_input, temp)
                similarity = compute_similarity(user_input, explanation)
                st.write(f"📊 New Similarity: {round(similarity,3)}")

            st.markdown("### ✨ Simplified Explanation")
            st.write(explanation)
