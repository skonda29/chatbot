import os
import sys
import logging

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

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.embeddings import HuggingFaceEmbedding
import nltk

# Download required NLTK data
nltk.download('punkt', download_dir='/tmp/nltk_data')
nltk.download('stopwords', download_dir='/tmp/nltk_data')

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

@app.get("/")
async def health_check():
    """Health check endpoint that also returns port information"""
    port = os.environ.get("PORT", "Not set")
    return {
        "status": "healthy",
        "port": port,
        "environment": {
            "NLTK_DATA": os.environ.get("NLTK_DATA"),
            "PORT": port
        }
    }

# Initialize the embedding model
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load documents and create index
logger.info("Loading documents and building index...")
documents = SimpleDirectoryReader('data').load_data()
index = VectorStoreIndex.from_documents(
    documents,
    embed_model=embed_model
)

@app.post("/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        query = data.get("message", "")
        if not query:
            return JSONResponse(
                status_code=400,
                content={"error": "No message provided"}
            )
        
        response = index.as_query_engine().query(query)
        return {"response": str(response)}
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Render requires PORT env variable
    uvicorn.run("main:app", host="0.0.0.0", port=port)
