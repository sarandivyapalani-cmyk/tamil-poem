import streamlit as st
from transformers import pipeline

@st.cache_resource
def load_model():
    # lightweight translation model
    return pipeline(
        "translation",
        model="facebook/nllb-200-distilled-600M"
    )

translator = load_model()

def convert_to_modern_tamil(text):
    result = translator(text, src_lang="tam_Taml", tgt_lang="tam_Taml")
    return result[0]["translation_text"]



