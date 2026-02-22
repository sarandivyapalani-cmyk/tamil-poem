import streamlit as st
import requests

# ==============================
# CONFIGURATION
# ==============================

SARVAM_API_KEY = st.secrets["SARVAM_API_KEY"]
SARVAM_URL = "https://api.sarvam.ai/v1/chat/completions"

st.set_page_config(page_title="Tamil Linguistic Simplification System", layout="wide")

st.title("AI-Driven Tamil Simplification & Linguistic Analysis System")

st.markdown("### Phase 1: Any Language → Deep Simple Tamil")
st.markdown("### Phase 2: Tamil → In-Depth Grammar + Explanation")

# ==============================
# USER INPUT
# ==============================

user_input = st.text_area("Enter Text Here:", height=200)

mode = st.radio(
    "Select Mode:",
    ("Phase 1: Language to Simple Tamil", 
     "Phase 2: Tamil Deep Linguistic Analysis")
)

# ==============================
# PROMPT GENERATION
# ==============================

def generate_prompt(text, mode):
    
    if mode == "Phase 1: Language to Simple Tamil":
        return f"""
You are a Tamil linguistic professor.

Convert the following text into deeply simplified Tamil.

Text:
{text}

Instructions:
1. Translate into Tamil if needed.
2. Provide very detailed simplified explanation.
3. Explain each sentence separately.
4. Use easy vocabulary suitable for school students.
5. Avoid generic AI style.
6. Provide structured headings.

Output Format:

### 1. எளிய தமிழ் மாற்றம்
...

### 2. வரி வாரியாக விளக்கம்
...

### 3. முக்கிய சொற்களின் விளக்கம்
Word | எளிய பொருள் | பயன்பாடு

### 4. கருத்து விளக்கம்
...

### 5. நடைமுறை பயன்பாடு
...
"""

    else:
        return f"""
You are a Tamil linguistic expert and grammar professor.

Analyze the following Tamil text deeply.

Text:
{text}

Instructions:
1. Provide detailed simplified meaning.
2. Explain line-by-line.
3. Break each word.
4. Classify grammar type:
   பெயர்ச்சொல், வினைச்சொல், உரிச்சொல், இடைச்சொல், பெயரடை, சுட்டுப்பெயர் etc.
5. Explain word meaning in simple Tamil.
6. Provide concept explanation.
7. Avoid generic AI style.
8. Use structured headings and tables.

Output Format:

### 1. எளிய விளக்கம்
...

### 2. வரி வாரியாக விளக்கம்
...

### 3. சொல் - இலக்கண அட்டவணை
Word | இலக்கண வகை | எளிய பொருள் | விளக்கம்

### 4. கருத்து விளக்கம்
...

### 5. பயன்பாட்டு சூழல்
...
"""

# ==============================
# API CALL FUNCTION
# ==============================

def call_sarvam(prompt):
    
    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "sarvam-m",
        "messages": [
            {"role": "system", "content": "You are a Tamil language expert."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    response = requests.post(SARVAM_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.text}"

# ==============================
# RUN BUTTON
# ==============================

if st.button("Analyze Text"):

    if user_input.strip() == "":
        st.warning("Please enter text.")
    else:
        with st.spinner("Processing..."):
            prompt = generate_prompt(user_input, mode)
            result = call_sarvam(prompt)
            st.markdown("---")
            st.markdown(result)


