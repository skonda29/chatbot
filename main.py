import os
import sys
import logging
import socket

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set environment variables before any other imports
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["NLTK_DATA"] = "/tmp/nltk_data"

# Import only what's needed initially
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Get port from environment with explicit fallback and logging
try:
    PORT = int(os.environ.get("PORT", "8000"))
    logger.info(f"PORT environment variable found: {PORT}")
except (ValueError, TypeError) as e:
    PORT = 8000
    logger.warning(f"Failed to get PORT from environment, using default: {PORT}. Error: {e}")

HOST = "0.0.0.0"

logger.info(f"Starting application with HOST={HOST} and PORT={PORT}")

# Create FastAPI app
app = FastAPI(
    title="ReachOut Chatbot API",
    description="Mental health chatbot with document Q&A capabilities",
    version="1.0.0"
)

# CORS middleware with minimal settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "HEAD"],
    allow_headers=["*"],
)

@app.get("/")
@app.head("/")
async def read_root():
    """Health check endpoint"""
    logger.info(f"Health check received. Running on port {PORT}")
    return {
        "status": "healthy",
        "port": PORT,
        "host": HOST,
        "environment": {
            "PORT": os.environ.get("PORT"),
            "HOST": os.environ.get("HOST")
        }
    }

@app.on_event("startup")
async def startup_event():
    """Initialize required modules at startup"""
    logger.info(f"Starting application on {HOST}:{PORT}")
    
    try:
        # Import remaining modules
        from models import ChatRequest
        from chat_engine import get_response
        from crisis import contains_crisis_keywords, SAFETY_MESSAGE
        from logger import log_chat
        from doc_engine import query_documents
        
        logger.info("Successfully loaded all required modules")
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        sys.exit(1)

@app.post("/chat")
async def chat_with_memory(request: Request):
    try:
        data = await request.json()
        chat_request = ChatRequest(**data)
        
        if contains_crisis_keywords(chat_request.query):
            log_chat(chat_request.session_id, chat_request.query, SAFETY_MESSAGE, is_crisis=True)
            return {"response": SAFETY_MESSAGE}

        response = get_response(chat_request.session_id, chat_request.query)
        log_chat(chat_request.session_id, chat_request.query, response, is_crisis=False)
        return {"response": response}
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/doc-chat")
async def chat_with_documents(request: Request):
    try:
        data = await request.json()
        response = query_documents(data.get("query", ""))
        return {"response": str(response)}
    except Exception as e:
        logger.error(f"Error in doc-chat endpoint: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    # For local development
    logger.info(f"Starting server on {HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
