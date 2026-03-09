# Diabetes Assistant

Локальный AI-ассистент для пациентов с диабетом.

## Что умеет
- отвечает на общие вопросы про диабет через LLM
- отвечает по документам через RAG
- ведет дневник сахара
- ведет дневник самочувствия
- показывает записи дневника
- анализирует последние записи сахара
- имеет emergency-ветку для потенциально опасных ситуаций

## Архитектура
- Gradio UI
- LLM router
- General QA через локальную LLM
- RAG по медицинским документам
- SQLite для дневника
- ChromaDB для retrieval

## Стек
- Python
- Gradio
- SQLite
- ChromaDB
- sentence-transformers
- Ollama
- Gemma 3 4B

## Примеры запросов
- запиши сахар 7.4 после ужина
- сегодня слабость и тошнота
- покажи мой сахар
- покажи симптомы
- проанализируй мой сахар
- что такое диабет 2 типа
- что такое неклассифицированный диабет

## Как запустить
```bash
git clone <repo_url>
cd diabetes_agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama run gemma3:4b
python app.py