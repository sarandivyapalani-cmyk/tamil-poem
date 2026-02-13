import streamlit as st
from model_loader import convert_to_modern_tamil

st.title("Ancient Tamil → Modern Tamil Converter")

st.write("Upload or paste Tamil poem (5+ lines supported)")

text = st.text_area("Enter Tamil poem")

if st.button("Convert"):

    if text.strip():

        lines = text.split("\n")

        st.write("### Output")

        for i, line in enumerate(lines):
            if line.strip():
                modern = convert_to_modern_tamil(line)

                st.write(f"Line {i+1}")
                st.write("Original:", line)
                st.write("Modern Tamil:", modern)
                st.write("---")


