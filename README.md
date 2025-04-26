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
