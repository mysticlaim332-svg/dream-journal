FROM python:3.12-slim

WORKDIR /app

# System deps (for audio processing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot/ .

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
