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

class ChatEngine:
    def __init__(self):
        self.responses = {
            "hello": "Hello! How can I help you today?",
            "how are you": "I'm doing well, thank you for asking. How are you feeling?",
            "help": "I'm here to help you with any mental health concerns or questions you may have. What's on your mind?",
            "stress": "I understand that stress can be overwhelming. Would you like to talk about what's causing your stress?",
            "anxiety": "It's normal to feel anxious sometimes. Can you tell me more about what you're experiencing?",
            "depression": "I'm here to listen and support you. Have you considered talking to a mental health professional about these feelings?",
        }
    
    def get_response(self, message: str) -> str:
        """
        Get a response based on the user's message.
        """
        message = message.lower().strip()
        
        # Check for exact matches first
        if message in self.responses:
            return self.responses[message]
            
        # Default response for unmatched messages
        return "I understand you're saying: " + message + ". I'm here to listen and support you. Would you like to tell me more about how you're feeling?"

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
