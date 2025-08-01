FROM python:3.9-slim  # Slim image

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --only-binary :all: -r requirements.txt  # Force wheels

COPY . .
CMD ["streamlit", "run", "app.py"]
