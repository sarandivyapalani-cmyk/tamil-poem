import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

@st.cache_resource
def load_model():
    model_name = "ai4bharat/indictrans2-indic-indic-dist-200M"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model

tokenizer, model = load_model()

def convert_to_modern_tamil(text):

    input_text = f"Convert classical Tamil to modern Tamil: {text}"

    inputs = tokenizer(input_text, return_tensors="pt", padding=True)
    outputs = model.generate(**inputs, max_length=256)

    return tokenizer.decode(outputs[0], skip_special_tokens=True)


