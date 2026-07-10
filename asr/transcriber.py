import os
import torch
import json
import time
from faster_whisper import WhisperModel
from pyannote.audio import Pipeline


class AudioTranscriber:
    def __init__(self, model_size: str = "medium"):
        print(f"Инициализация модели Whisper ({model_size})...")

        self.whisper = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",
            download_root="/root/.cache/huggingface"
        )

        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            print("ВНИМАНИЕ: HF_TOKEN не найден в окружении! Диаризация отключена.")
            self.diarization_pipeline = None
        else:
            print("Инициализация Pyannote Diarization (может занять время при первом запуске)...")
            self.diarization_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                token=hf_token
            )
            self.diarization_pipeline.to(torch.device("cpu"))

        print("✅ Все ASR-модели успешно загружены.\n")

    def transcribe(self, audio_path: str) -> list[dict]:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Файл {audio_path} не найден.")

        print(f"▶️ [Шаг 1/3] Whisper: транскрибация файла {audio_path}...")
        segments, info = self.whisper.transcribe(audio_path, beam_size=5, language="ru")
        whisper_segments = list(segments)  # Вычитываем генератор, чтобы зафиксировать текст
        print(f"   ✓ Язык: {info.language} (уверенность: {round(info.language_probability * 100)}%)")

        print(f"▶️ [Шаг 2/3] Pyannote: разделение по голосам (диаризация)...")
        diarization = None
        if self.diarization_pipeline:
            diarization = self.diarization_pipeline(audio_path)

        print(f"▶️ [Шаг 3/3] Слияние текста и спикеров...")
        transcript = []

        for segment in whisper_segments:
            start = round(segment.start, 2)
            end = round(segment.end, 2)
            text = segment.text.strip()
            speaker = "Неизвестно"

            if diarization:
                max_intersection = 0.0
                for turn, _, spk in diarization.speaker_diarization.itertracks(yield_label=True):
                    intersection = min(end, turn.end) - max(start, turn.start)
                    if intersection > max_intersection:
                        max_intersection = intersection
                        speaker = spk

            if speaker == "SPEAKER_00":
                speaker = "Оператор"
            elif speaker == "SPEAKER_01":
                speaker = "Клиент"

            transcript.append({
                "speaker": speaker,
                "start": start,
                "end": end,
                "text": text
            })

        return transcript


if __name__ == "__main__":
    TEST_AUDIO = "test_data/call_dialog.m4a"

    if not os.path.exists(TEST_AUDIO):
        print(f"\n❌ Ошибка: Файл {TEST_AUDIO} не найден!")
        print("Убедись, что файл лежит в папке test_data на твоем компьютере.")
        exit(1)

    print("\n🚀 Запуск тестового прогона ASR Pipeline...")
    start_time = time.time()

    try:
        transcriber = AudioTranscriber(model_size="medium")

        result = transcriber.transcribe(TEST_AUDIO)

        print("\n✅ Транскрибация успешно завершена!")
        print(f"⏱️ Время выполнения: {round(time.time() - start_time, 2)} сек.\n")

        # Выводим результат
        print("Результат:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"\n❌ Ошибка во время выполнения: {e}")
