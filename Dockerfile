# Dockerfile
FROM python:3.13.5-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY utility ./utility
COPY main.py .

CMD ["python", "main.py"]