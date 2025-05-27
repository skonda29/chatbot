import os
import sys

# Set environment variables before any other imports
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["NLTK_DATA"] = "/tmp/nltk_data"

# Import only what's needed initially
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get port from environment with fallback
PORT = int(os.getenv("PORT", 10000))

# Create FastAPI app
app = FastAPI(
    title="ReachOut Chatbot API",
    description="Mental health chatbot with document Q&A capabilities",
    version="1.0.0",
    docs_url=None,  # Disable docs to save memory
    redoc_url=None  # Disable redoc to save memory
)

# CORS middleware with minimal settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "HEAD"],  # Added HEAD for health checks
    allow_headers=["*"],
)

@app.get("/")
@app.head("/")  # Added HEAD endpoint for health checks
def read_root():
    """Health check endpoint"""
    return {"status": "ok"}  # Simplified response

# Initialize required modules at startup
try:
    from models import ChatRequest
    from chat_engine import get_response
    from crisis import contains_crisis_keywords, SAFETY_MESSAGE
    from logger import log_chat
    from doc_engine import query_documents
except ImportError as e:
    print(f"Failed to import required modules: {e}")
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
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
