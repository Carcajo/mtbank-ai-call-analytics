import os
import requests
from pydantic import BaseModel

class Pipeline:
    class Valves(BaseModel):
        # Внутри Docker-сети бэкенд доступен по имени контейнера
        API_URL: str = "http://mtbank-ai-backend:8000/analyze"

    def __init__(self):
        self.type = "pipe"
        self.id = "mtbank_call_analyzer"
        self.name = "MTBank Call Analyzer 🤖"
        self.valves = self.Valves()

    async def on_startup(self):
        print(f"[{self.name}] Пайплайн успешно инициализирован.")

    def pipe(self, user_message: str, model_id: str, messages: list, body: dict):
        file_path = user_message.strip()
        
        # Проверяем, видит ли пайплайн аудиофайл
        if not os.path.exists(file_path):
            yield f"❌ **Ошибка:** Файл `{file_path}` не найден. Проверьте путь (например: test_data/call_dialog.m4a)."
            return

        yield "Начинаю анализ аудиофайла... ⏳ Это займет около 1-2 минут.\n\n"
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'audio/mpeg')}
                response = requests.post(self.valves.API_URL, files=files, timeout=300)
            
            if response.status_code != 200:
                yield f"❌ Ошибка бэкенда (код {response.status_code}):\n{response.text}"
                return
                
            data = response.json()
            
            # Рендерим Markdown-отчет
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
            
        except requests.exceptions.RequestException as e:
            yield f"❌ Ошибка сети при запросе к FastAPI: `{str(e)}`"
        except Exception as e:
            yield f"❌ Системная ошибка пайплайна: `{str(e)}`"
