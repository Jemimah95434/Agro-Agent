FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir gunicorn

COPY backend/ /app/
COPY models/ /models/
COPY datasets/ /datasets/

ENV MODEL_PATH=/models

EXPOSE 10000
CMD ["sh", "-c", "gunicorn agro_backend.wsgi:application --bind 0.0.0.0:${PORT:-10000} --workers 1 --timeout 180"]
