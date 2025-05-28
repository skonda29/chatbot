#!/bin/bash
echo "Starting application..."
echo "PORT: $PORT"
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"

# Download NLTK data
python -c "import nltk; nltk.download('punkt', download_dir='/tmp/nltk_data'); nltk.download('stopwords', download_dir='/tmp/nltk_data')"

# Start the application
exec python -m uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 --log-level debug 