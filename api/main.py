import os
import shutil
import tempfile
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from asr.transcriber import AudioTranscriber
from agents.graph import run_agentic_analysis

transcriber_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global transcriber_service
    print("⏳ [Lifespan] Загрузка ML-моделей в память сервера...")
    try:
        transcriber_service = AudioTranscriber(model_size="medium")
        print("✅ [Lifespan] Модели успешно загружены и готовы к работе.")
    except Exception as e:
        print(f"❌ [Lifespan] Ошибка загрузки моделей: {e}")

    yield

    print("🛑 [Lifespan] Остановка сервера, очистка ресурсов...")
    transcriber_service = None


app = FastAPI(title="MTBank AI Analytics API", lifespan=lifespan)


@app.post("/analyze")
def analyze_audio(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Файл не передан")

    ext = os.path.splitext(file.filename)[1].lower()
    allowed_exts = {".wav", ".mp3", ".ogg", ".m4a", ".flac"}
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Неподдерживаемый формат. Разрешены: {allowed_exts}")

    if not transcriber_service:
        raise HTTPException(status_code=503, detail="ASR сервис еще инициализируется, попробуйте позже")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_audio:
            shutil.copyfileobj(file.file, temp_audio)
            temp_audio_path = temp_audio.name

        print(f"📥 Получен запрос на анализ файла: {file.filename}")

        transcript = transcriber_service.transcribe(temp_audio_path)

        os.remove(temp_audio_path)

        final_analysis = run_agentic_analysis(transcript)

        return JSONResponse(content=final_analysis)

    except Exception as e:
        if 'temp_audio_path' in locals() and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        print(f"❌ Ошибка при обработке эндпоинта: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/models")
async def models():
    return {
        "object": "list",
        "data": [{"id": "mtbank-ai-agent", "object": "model", "created": 1677610602, "owned_by": "mtbank"}]
    }


@app.get("/")
async def root():
    return {"status": "healthy", "service": "MTBank Multi-Agent Backend"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    