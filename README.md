# Diabetes Assistant

Локальный AI-ассистент для самоконтроля диабета.

Проект демонстрирует архитектуру AI-ассистента с использованием LLM, RAG и инструментов (tools) для работы с пользовательскими данными. Ассистент умеет отвечать на вопросы о диабете, хранить данные о концентрации сахара в крови и строить по ним график,записывать самочувствие пациента и анализировать измерения.

---

# Возможности

- отвечает на общие вопросы про диабет через локальную LLM  
- использует RAG для ответов по медицинским документам  
- ведет дневник сахара  
- ведет дневник самочувствия  
- показывает записи дневника  
- анализирует последние записи сахара  
- строит график сахара  
- имеет emergency-ветку для потенциально опасных ситуаций  

---

# Архитектура

**Pipeline работы ассистента:**

1. **User**
2. **Gradio UI**
3. **LLM Router**
4. **Tool Layer**
   - glucose diary
   - symptom diary
   - analytics
   - knowledge (RAG)
5. **Vector Search (ChromaDB)**
6. **Local LLM (Gemma 3 4B через Ollama)**
---

# Технологии

- Python  
- Gradio  
- SQLite  
- ChromaDB  
- sentence-transformers  
- Ollama  
- Gemma 3 4B  

---

# Примеры запросов

- запиши сахар 7.4 после ужина
- сегодня слабость и тошнота
- покажи мой сахар
- покажи симптомы
- проанализируй мой сахар
- что такое диабет 2 типа
- что такое неклассифицированный диабет
---

# Метрики

Initial internal evaluation:

- Router accuracy: **100%**
- RAG retrieval hit@2: **100%**
- LLM-as-a-judge (8 тестовых кейсов):
  - Correctness: **100%**
  - Safety: **100%**
  - Clarity: **100%**
  - Usefulness: **100%**

Метрики получены на небольшом ручном наборе тестовых запросов и используются как sanity-check для MVP.

---

## Как запустить
```bash
git clone <repo_url>
cd diabetes_agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama run gemma3:4b
python app.py
