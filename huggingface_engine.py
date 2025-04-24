import os
os.environ["TRANSFORMERS_NO_TF"] = "1"
from transformers import AutoTokenizer, AutoModelForCausalLM

# Use smaller GPT-2 model (124M params)
tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")  # smaller than 'gpt2-large'

def generate_response(prompt: str) -> str:
    inputs = tokenizer(prompt, return_tensors="pt")
    
    # Limit generation to max 50 new tokens
    outputs = model.generate(
        inputs["input_ids"], 
        max_new_tokens=50,
        do_sample=True,  # adds randomness
        temperature=0.7  # controls creativity
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response
