import os
import requests
import re
import tempfile
from pydantic import BaseModel


class Pipeline:
    class Valves(BaseModel):
        API_URL: str = "http://mtbank-ai-backend:8000/analyze"

    def __init__(self):
        self.type = "pipe"
        self.id = "mtbank_call_analyzer"
        self.name = "MTBank Call Analyzer 🤖"
        self.valves = self.Valves()

    async def on_startup(self):
        print(f"[{self.name}] Пайплайн успешно инициализирован.")

    def pipe(self, user_message: str, model_id: str, messages: list, body: dict):
        file_path = None
        is_temp_file = False

        yield "Начинаю обработку запроса... ⏳\n\n"

        try:
            files_data = body.get("messages", [])[-1].get("files", []) if body.get("messages") else []

            if files_data:
                yield "📎 Обнаружен прикрепленный файл. Извлекаю...\n\n"
                first_file = files_data[0]
                if isinstance(first_file, dict) and "url" in first_file:
                    file_path = first_file["url"].replace("file://", "")
                elif isinstance(first_file, dict) and "path" in first_file:
                    file_path = first_file["path"]

            elif "http" in user_message:
                url_match = re.search(r'(https?://\S+)', user_message)
                if url_match:
                    download_url = url_match.group(1)
                    yield f"📥 Обнаружена ссылка. Скачиваю аудиофайл...\n\n"

                    response = requests.get(download_url, stream=True, timeout=30)
                    response.raise_for_status()

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as tmp_file:
                        for chunk in response.iter_content(chunk_size=8192):
                            tmp_file.write(chunk)
                        file_path = tmp_file.name
                    is_temp_file = True

            else:
                file_path = user_message.strip()

            if not file_path or not os.path.exists(file_path):
                yield f"❌ **Ошибка:** Файл не найден. Пожалуйста, прикрепите файл к сообщению (через значок скрепки) или отправьте прямую HTTP-ссылку."
                return

            yield "🚀 Файл готов. Отправляю на бэк... (Это займет около 1-2 минут)\n\n"

            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'audio/mpeg')}
                response = requests.post(self.valves.API_URL, files=files, timeout=300)

            if is_temp_file and os.path.exists(file_path):
                os.remove(file_path)

            if response.status_code != 200:
                yield f"❌ Ошибка бэкенда (код {response.status_code}):\n{response.text}"
                return

            data = response.json()

            md = f"### 📊 Результаты анализа звонка\n\n"
            md += f"**Тематика:** {data['classification']['topic']}\n"
            priority = data['classification']['priority']
            p_color = "🔴" if priority in ["high", "critical"] else ("🟡" if priority == "medium" else "🟢")
            md += f"**Приоритет:** {p_color} {priority.upper()}\n\n"

            md += f"### ⭐ Оценка качества: {data['quality_score']['total']}/100\n"
            checklist = data['quality_score']['checklist']
            md += f"- Приветствие: {'✅' if checklist.get('greeting') else '❌'}\n"
            md += f"- Выявление проблемы: {'✅' if checklist.get('need_detection') else '❌'}\n"
            md += f"- Решение: {'✅' if checklist.get('solution_provided') else '❌'}\n"
            md += f"- Прощание: {'✅' if checklist.get('farewell') else '❌'}\n\n"

            md += f"### 🛡️ Комплаенс (Безопасность): {'✅ Пройден' if data['compliance']['passed'] else '❌ Нарушения'}\n"
            if not data['compliance']['passed']:
                for issue in data['compliance']['issues']:
                    md += f"> 🚨 *{issue}*\n"
            md += "\n\n"

            md += f"### 📝 Резюме\n{data['summary']}\n\n"

            if data['action_items']:
                md += "### ⚡ Action Items\n"
                for item in data['action_items']:
                    md += f"- [ ] {item}\n"

            yield md

        except Exception as e:
            if is_temp_file and file_path and os.path.exists(file_path):
                os.remove(file_path)
            yield f"❌ Системная ошибка пайплайна: `{str(e)}`"
