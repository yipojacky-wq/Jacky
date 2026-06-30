FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY static ./static
COPY demo ./demo

ENV APP_STORAGE_PATH=/tmp/disclosure-completion-cases.json
ENV APP_DEMO_MODE=false

EXPOSE 8010

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8010}"]
