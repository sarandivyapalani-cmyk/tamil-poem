from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load IndicTrans2 model (Tamil support)
model_name = "ai4bharat/indictrans2-en-indic-1B"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def convert_to_modern_tamil(text):

    # Prompt telling AI what to do
    input_text = f"Convert classical Tamil to modern Tamil: {text}"

    inputs = tokenizer(input_text, return_tensors="pt", padding=True)

    outputs = model.generate(**inputs, max_length=200)

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return result
