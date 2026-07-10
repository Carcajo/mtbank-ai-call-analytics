import os
import re
import jiwer
from asr.transcriber import AudioTranscriber


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def run_evaluation():
    print("🎙️ Запуск оценки качества ASR (Расчет Word Error Rate)...")
    transcriber = AudioTranscriber(model_size="medium")

    test_data_dir = "test_data"
    if not os.path.exists(test_data_dir):
        print(f"❌ Папка {test_data_dir} не найдена!")
        return

    audio_extensions = (".wav", ".mp3", ".ogg", ".m4a")
    audio_files = [f for f in os.listdir(test_data_dir) if f.endswith(audio_extensions)]

    if not audio_files:
        print("⚠️ В папке test_data не найдено аудиофайлов для оценки.")
        return

    results = []
    total_wer = 0.0
    evaluated_count = 0

    for audio_file in audio_files:
        base_name = os.path.splitext(audio_file)[0]
        txt_file = f"{base_name}.txt"
        txt_path = os.path.join(test_data_dir, txt_file)
        audio_path = os.path.join(test_data_dir, audio_file)
        if not os.path.exists(txt_path):
            print(f"⏩ Пропуск {audio_file}: нет эталонного файла {txt_file}")
            continue

        print(f"       Обработка: {audio_file}...")
        with open(txt_path, "r", encoding="utf-8") as f:
            reference_raw = f.read()

        try:
            transcript_segments = transcriber.transcribe(audio_path)
            hypothesis_raw = " ".join([seg["text"] for seg in transcript_segments])

            reference = normalize_text(reference_raw)
            hypothesis = normalize_text(hypothesis_raw)

            if not reference and not hypothesis:
                wer = 0.0
            else:
                wer = jiwer.wer(reference, hypothesis)

            results.append({
                "file": audio_file,
                "wer": wer,
                "status": "Success"
            })
            total_wer += wer
            evaluated_count += 1

        except Exception as e:
            print(f"❌ Ошибка обработки файла {audio_file}: {e}")
            results.append({
                "file": audio_file,
                "wer": 1.0,
                "status": f"Error: {str(e)}"
            })
    print("\n" + "=" * 50)
    print("📊 ИТОГОВАЯ ТАБЛИЦА WER ДЛЯ README.md")
    print("=" * 50 + "\n")

    print("| Аудиофайл | Метрика WER | Статус обработки |")
    print("| :--- | :---: | :--- |")
    for res in results:
        wer_display = f"{round(res['wer'] * 100, 2)}%" if res['status'] == "Success" else "—"
        print(f"| {res['file']} | {wer_display} | {res['status']} |")

    if evaluated_count > 0:
        average_wer = round((total_wer / evaluated_count) * 100, 2)
        print(r"| **Средний WER по датасету** | **" + f"{average_wer}%" + r"** | |")


if __name__ == "__main__":
    run_evaluation()
