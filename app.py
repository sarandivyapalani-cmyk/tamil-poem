import streamlit as st
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

@st.cache_resource
def load_model():
    model_name = "google/flan-t5-base"
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    return tokenizer, model

tokenizer, model = load_model()

def explain_tamil_poem(poem_text):
    prompt = f"""
Explain the following Tamil poem in modern Tamil.
Give:
1. Summary
2. Line-by-line explanation
3. Literary elements

Poem:
{poem_text}
"""

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    outputs = model.generate(
        **inputs,
        max_new_tokens=300
    )
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return result

st.title("📜 Tamil Poem Explainer")
st.write("Upload or paste any Tamil poem to get explanation.")

poem_input = st.text_area("Enter Tamil Poem")

if st.button("Explain"):
    if poem_input.strip() == "":
        st.warning("Please enter a poem.")
    else:
        with st.spinner("Analyzing..."):
            explanation = explain_tamil_poem(poem_input)
            st.write(explanation)
