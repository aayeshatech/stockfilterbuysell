FROM python:3.9-slim
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev
COPY requirements.txt .
RUN pip install --no-cache-dir --only-binary :all: -r requirements.txt
