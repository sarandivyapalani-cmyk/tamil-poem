import streamlit as st
from transformers import pipeline

@st.cache_resource
def load_pipeline():
    return pipeline(
        "text2text-generation",
        model="google/flan-t5-small"
    )

generator = load_pipeline()

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
    result = generator(prompt, max_new_tokens=200)
    return result[0]["generated_text"]

st.title("📜 Tamil Poem Explainer")
st.write("Paste any Tamil poem and get explanation.")

poem_input = st.text_area("Enter Tamil Poem")

if st.button("Explain"):
    if poem_input.strip() == "":
        st.warning("Please enter a poem.")
    else:
        with st.spinner("Analyzing..."):
            explanation = explain_tamil_poem(poem_input)
            st.write(explanation)

