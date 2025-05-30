# ReachOut – Mental Health Chatbot Backend

This is the backend engine powering ReachOut, an AI-driven mental health chatbot designed to provide empathetic support, document-based Q&A, and crisis detection. The backend integrates multiple AI models and services to enable safe, responsive, and intelligent mental health assistance.

---

## Features

- **Conversational Engine**: Uses Gemini API for empathetic responses to user queries.
- **Document Q&A Engine**: Powered by LlamaIndex, enabling document retrieval and answering based on mental health resources.
- **Crisis Detection Module**: Scans user input for crisis-related signals and triggers automated safety protocols.
- **HuggingFace Embeddings**: Generates semantic embeddings for queries to enhance document retrieval.
- **Custom Logging**: Tracks user sessions and logs interactions for auditing and safety purposes.

---

## Tech Stack

- **Framework**: FastAPI (Python)
- **AI Integrations**:
  - Gemini API (chat responses)
  - LlamaIndex (document querying)
  - HuggingFace Sentence Transformers (embeddings)
- **Natural Language Toolkit (NLTK)**: Tokenization and text preprocessing.
- **Logging**: Custom logging system for auditing interactions.

## Setup Instructions

### Clone the repository
```bash
git clone https://github.com/your-username/reachout-backend.git
cd reachout-backend
```
### Set up a virtual environment (recommended)

#### For Linux / Mac:
```bash
python -m venv venv
source venv/bin/activate
```
#### For Windows:
```bash
python -m venv venv
venv\Scripts\activate
```
### Install dependencies
```bash
pip install -r requirements.txt
```
### Run the FastAPI server
```bash
uvicorn main:app --reload
```

## Environment Variables

The following environment variables need to be set in AWS Amplify:

```bash
# Python Runtime
PYTHON_VERSION=3.9.12

# Application Settings
PORT=8080
NLTK_DATA=/tmp/nltk_data

# Model Settings
TRANSFORMERS_NO_TF=1
TOKENIZERS_PARALLELISM=false
```

## Deployment

1. AWS Amplify Console Setup:
   - Go to App settings → Environment variables
   - Add all required environment variables
   - Build settings will use amplify.yml
   - Monitor builds in the Deploy tab

2. Custom Domain (Optional):
   - Set up in Domain management
   - SSL certificate provided automatically

3. Monitoring:
   - View logs in Deploy tab
   - Real-time monitoring in App settings → Monitoring
