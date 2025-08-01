# Start with official Python 3.9 slim image
FROM python:3.9-slim

# Set up environment
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=yes \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install only essential build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgomp1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install requirements (using Polars instead of Pandas)
COPY requirements.txt .
RUN pip install --only-binary=:all: --no-deps -r requirements.txt

# Copy app files
COPY . .

# Run the app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
