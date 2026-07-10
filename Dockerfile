FROM python:3.11-slim

# Установка системных зависимостей для обработки аудио и сборки пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app


RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi \
    uvicorn \
    python-multipart \
    pydantic \
    faster-whisper \
    requests \
    pyannote.audio \
    torch \
    torchaudio \
    langgraph \
    langchain-openai \
    pytest \
    jiwer \
    --extra-index-url https://download.pytorch.org/whl/cpu

# Копируем исходный код приложения
COPY . .

# Открываем порт для FastAPI / OpenWebUI Pipelines
EXPOSE 8000

# Команда для запуска (пока запускаем базовый FastAPI, потом адаптируем под Pipelines)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]