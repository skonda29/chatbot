#!/bin/bash
echo "Starting application..."
echo "PORT: $PORT"
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Network interfaces:"
ifconfig || ip addr

# Download NLTK data
python -c "import nltk; nltk.download('punkt', download_dir='/tmp/nltk_data'); nltk.download('stopwords', download_dir='/tmp/nltk_data')"

# Check if port is already in use
nc -z 0.0.0.0 ${PORT:-10000} 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Warning: Port ${PORT:-10000} is already in use"
    # List processes using the port
    lsof -i :${PORT:-10000} || netstat -tulpn 2>/dev/null | grep ${PORT:-10000}
fi

# Start the application with explicit port binding
echo "Starting uvicorn on port ${PORT:-10000}..."
exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000} --workers 1 --log-level debug 