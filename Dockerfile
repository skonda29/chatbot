FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create NLTK data directory
RUN mkdir -p /tmp/nltk_data

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    TRANSFORMERS_NO_TF=1 \
    TOKENIZERS_PARALLELISM=false \
    NLTK_DATA=/tmp/nltk_data \
    PORT=10000

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt', download_dir='/tmp/nltk_data'); nltk.download('stopwords', download_dir='/tmp/nltk_data')"

# Expose port
EXPOSE ${PORT}

# Start the application with gunicorn
CMD gunicorn -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${PORT} main:app --timeout 120 --log-level debug 