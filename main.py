import os
import sys
import logging
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["NLTK_DATA"] = "/tmp/nltk_data"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv
from models import ChatRequest
from chat_engine import get_response
from crisis import contains_crisis_keywords, SAFETY_MESSAGE
from logger import log_chat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# FastAPI app
app = FastAPI(
    title="ReachOut Chatbot API",
    description="Mental health chatbot with crisis detection and AI support",
    version="1.0.0"
)

# CORS middleware - allow all origins for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for frontend integration
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def read_root():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ReachOut Chatbot API</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .container {
                max-width: 800px;
                margin: 40px auto;
                padding: 40px;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 16px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                color: #333;
            }
            h1 {
                color: #4c51bf;
                margin-bottom: 30px;
                font-size: 2.5em;
                text-align: center;
            }
            .feature {
                background: #f7fafc;
                padding: 20px;
                margin: 20px 0;
                border-radius: 12px;
                border-left: 6px solid #4c51bf;
            }
            .endpoint {
                background: #e6fffa;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 4px solid #38b2ac;
            }
            code {
                background: #edf2f7;
                padding: 4px 8px;
                border-radius: 4px;
                font-family: 'Monaco', 'Menlo', monospace;
                color: #d53f8c;
            }
            .status {
                text-align: center;
                background: #48bb78;
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 30px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="status">✅ ReachOut Chatbot API is Running!</div>
            <h1>🤖 ReachOut Mental Health Chatbot</h1>
            <p style="text-align: center; font-size: 1.1em; margin-bottom: 40px;">
                AI-powered mental health support with crisis detection
            </p>
            
            <div class="feature">
                <h3>🛡️ Crisis Detection & Safety</h3>
                <p>Automatic detection of crisis keywords with immediate safety resources</p>
            </div>
            
            <div class="feature">
                <h3>🧠 AI-Powered Conversations</h3>
                <p>Session-based conversations with empathetic responses powered by Gemini AI</p>
            </div>
            
            <div class="feature">
                <h3>📊 Chat Logging</h3>
                <p>Secure conversation logging for analysis and improvement</p>
            </div>
            
            <h2>API Endpoints:</h2>
            
            <div class="endpoint">
                <h4>POST /chat</h4>
                <p>Main chat endpoint with crisis detection</p>
                <code>{"session_id": "user123", "query": "I feel anxious"}</code>
            </div>
            
            <div class="endpoint">
                <h4>POST /doc-chat</h4>
                <p>Document-based chat for specific mental health topics</p>
                <code>{"session_id": "user123", "query": "stress management tips"}</code>
            </div>
            
            <div class="endpoint">
                <h4>GET /health</h4>
                <p>Health check endpoint</p>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ReachOut Chatbot API",
        "version": "1.0.0",
        "features": ["crisis_detection", "ai_chat", "session_management", "logging"]
    }

@app.post("/chat")
def chat_with_memory(request: ChatRequest):
    try:
        session_id = request.session_id
        user_query = request.query
        
        # Crisis check
        if contains_crisis_keywords(user_query):
            log_chat(session_id, user_query, SAFETY_MESSAGE, is_crisis=True)
            return {"response": SAFETY_MESSAGE}
        
        # Get chatbot response
        response = get_response(session_id, user_query)
        log_chat(session_id, user_query, response, is_crisis=False)
        
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "message": str(e)}
        )

@app.post("/doc-chat")
def chat_with_documents(request: ChatRequest):
    try:
        # Import here to avoid startup issues if doc_engine has problems
        from doc_engine import query_documents
        response = query_documents(request.query)
        return {"response": str(response)}
    except ImportError:
        logger.warning("doc_engine not available, falling back to regular chat")
        return chat_with_memory(request)
    except Exception as e:
        logger.error(f"Error in doc-chat endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Document chat unavailable", "message": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
