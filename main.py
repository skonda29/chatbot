import os
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Now, your other imports
from fastapi import FastAPI, Request
from doc_engine import query_documents
from fastapi import FastAPI
from dotenv import load_dotenv
from models import ChatRequest
from chat_engine import get_response
from crisis import contains_crisis_keywords, SAFETY_MESSAGE
from logger import log_chat
from doc_engine import query_documents
from fastapi.middleware.cors import CORSMiddleware
from metrics import MetricsCollector
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import asyncio
import subprocess
import sys

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

# Load environment variables first
load_dotenv()

# Get port from environment with fallback
PORT = int(os.getenv("PORT", 10000))

# Create FastAPI app
app = FastAPI(
    title="ReachOut Chatbot API",
    description="Mental health chatbot with document Q&A capabilities",
    version="1.0.0"
)

# Initialize metrics collector with reduced memory footprint
metrics = MetricsCollector()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# CORS middleware - update this with your web application's domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://localhost:3000", 
        os.getenv("FRONTEND_URL", ""),
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    response_time = time.time() - start_time
    
    # Record request metrics
    metrics.record_request(
        endpoint=str(request.url.path),
        response_time=response_time,
        status_code=response.status_code
    )
    
    return response

# Background task to record system metrics
async def record_system_metrics():
    while True:
        metrics.record_system_metrics()
        await asyncio.sleep(60)  # Record every minute

async def run_endpoint_tests():
    """Run the endpoint tests in the background"""
    await asyncio.sleep(2)  # Wait for server to fully start
    try:
        subprocess.Popen([sys.executable, "test_endpoints.py"])
    except Exception as e:
        print(f"Error running endpoint tests: {e}")

@app.on_event("startup")
async def startup_event():
    # Start system metrics collection
    asyncio.create_task(record_system_metrics())
    # Start endpoint testing
    asyncio.create_task(run_endpoint_tests())

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/dashboard")
def get_dashboard():
    return FileResponse("static/metrics_dashboard.html")

@app.get("/metrics")
def get_metrics():
    return metrics.get_summary()

@app.post("/chat")
def chat_with_memory(request: ChatRequest):
    session_id = request.session_id
    user_query = request.query
    
    if contains_crisis_keywords(user_query):
        log_chat(session_id, user_query, SAFETY_MESSAGE, is_crisis=True)
        return {"response": SAFETY_MESSAGE}

    response = get_response(session_id, user_query)
    log_chat(session_id, user_query, response, is_crisis=False)
    return {"response": response}

@app.post("/doc-chat")
def chat_with_documents(request: ChatRequest):
    response = query_documents(request.query)
    return {"response": str(response)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
