import os
os.environ["TRANSFORMERS_NO_TF"] = "1"
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not found. Check the .env file.")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Choose model (flash = faster, pro = better)
model = genai.GenerativeModel("gemini-1.5-flash")

# Session memory for chat history
session_memory_map = {}

def get_response(session_id: str, user_query: str):
    # Initialize chat history for session
    if session_id not in session_memory_map:
        session_memory_map[session_id] = []

    session_memory_map[session_id].append({"role": "user", "parts": [user_query]})

    # Wrap the latest user query in an empathetic prompt
    prompt = (
        "You are a kind and supportive mental health assistant. "
        "Respond with empathy and offer thoughtful advice or comfort. "
        "Here's what the user shared:\n\n"
        f"{user_query}\n\n"
        "Please provide a gentle, caring response."
    )

    # Add the wrapped prompt as the last user message
    session_memory_map[session_id][-1] = {"role": "user", "parts": [prompt]}

    # Generate response with full history
    response = model.generate_content(session_memory_map[session_id])

    # Append model response to history
    session_memory_map[session_id].append({"role": "model", "parts": [response.text]})

    return response.text
