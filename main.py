import os
import sys
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import nltk
from models import ChatRequest
from chat_engine import ChatEngine

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Set environment variables before any other imports
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["NLTK_DATA"] = "/tmp/nltk_data"

# Create FastAPI app
app = FastAPI(
    title="ReachOut Chatbot API",
    description="Mental health chatbot with document Q&A capabilities",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the directory of the current file
BASE_DIR = Path(__file__).resolve().parent

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize chat engine
chat_engine = ChatEngine()

# Download required NLTK data on startup
try:
    nltk.download('punkt', download_dir='/tmp/nltk_data')
    nltk.download('stopwords', download_dir='/tmp/nltk_data')
except Exception as e:
    logger.warning(f"Could not download NLTK data: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
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
            .endpoint {
                background: #f7fafc;
                padding: 20px;
                margin: 20px 0;
                border-radius: 12px;
                border-left: 6px solid #4c51bf;
                transition: transform 0.2s;
            }
            .endpoint:hover {
                transform: translateY(-2px);
            }
            .endpoint h3 {
                margin: 0 0 15px 0;
                color: #2d3748;
                font-size: 1.3em;
            }
            .endpoint p {
                margin: 8px 0;
                color: #4a5568;
                line-height: 1.6;
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
            .test-section {
                background: #bee3f8;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
                color: #2d3748;
            }
            button {
                background: #4c51bf;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px 5px;
            }
            button:hover {
                background: #3c4fd3;
            }
            #response {
                background: #f7fafc;
                padding: 15px;
                border-radius: 8px;
                margin-top: 15px;
                min-height: 50px;
                border: 1px solid #e2e8f0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="status">✅ ReachOut Chatbot API is Running!</div>
            <h1>🤖 ReachOut Chatbot API</h1>
            <p style="text-align: center; font-size: 1.1em; margin-bottom: 40px;">
                Welcome to the ReachOut Mental Health Chatbot API. Test the endpoints below:
            </p>
            
            <div class="endpoint">
                <h3>🏥 Health Check</h3>
                <p><strong>GET</strong> /health</p>
                <p>Check if the API is running and view system information</p>
                <button onclick="testHealth()">Test Health Endpoint</button>
            </div>
            
            <div class="endpoint">
                <h3>💬 Chat Endpoint</h3>
                <p><strong>POST</strong> /chat</p>
                <p>Send a message: <code>{"message": "your message here"}</code></p>
                <p>Get supportive responses for mental health conversations</p>
                <button onclick="testChat()">Test Chat Endpoint</button>
            </div>
            
            <div class="test-section">
                <h3>API Response:</h3>
                <div id="response">Click a button above to test the API endpoints</div>
            </div>
        </div>
        
        <script>
            async function testHealth() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    document.getElementById('response').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    document.getElementById('response').innerHTML = 'Error: ' + error.message;
                }
            }
            
            async function testChat() {
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({message: 'Hello, I need someone to talk to'})
                    });
                    const data = await response.json();
                    document.getElementById('response').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    document.getElementById('response').innerHTML = 'Error: ' + error.message;
                }
            }
        </script>
    </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    """Health check endpoint that also returns port information"""
    port = os.environ.get("PORT", "Not set")
    return {
        "status": "healthy",
        "service": "ReachOut Chatbot API",
        "version": "1.0.0",
        "port": port,
        "environment": {
            "NLTK_DATA": os.environ.get("NLTK_DATA"),
            "PORT": port
        }
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = chat_engine.get_response(request.message)
        return JSONResponse(content={"response": response})
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "message": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
