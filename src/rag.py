from pathlib import Path
import json
import urllib.request

import chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader


DATA_DIR = Path("data")
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "diabetes_knowledge"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"

_embedding_model = None
_collection = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
    return _embedding_model


def get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return _collection


def split_text(text: str, chunk_size: int = 700, overlap: int = 120):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def load_documents():
    docs = []

    for path in DATA_DIR.rglob("*"):
        if path.is_dir():
            continue

        if path.suffix.lower() in {".txt", ".md"}:
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue

        elif path.suffix.lower() == ".pdf":
            try:
                reader = PdfReader(path)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            except Exception:
                continue
        else:
            continue

        if not text.strip():
            continue

        chunks = split_text(text)

        for i, chunk in enumerate(chunks):
            docs.append({
                "id": f"{path.stem}_{i}",
                "text": chunk,
                "source": str(path.relative_to(DATA_DIR))
            })

    return docs


def build_rag_index():
    docs = load_documents()
    if not docs:
        return 0

    collection = get_collection()
    model = get_embedding_model()

    if collection.count() > 0:
        return collection.count()

    texts = [doc["text"] for doc in docs]
    ids = [doc["id"] for doc in docs]
    metadatas = [{"source": doc["source"]} for doc in docs]
    embeddings = model.encode(texts).tolist()

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings,
    )
    return len(docs)


def retrieve_context(query: str, top_k: int = 3, max_distance: float = 1.2):
    collection = get_collection()
    if collection.count() == 0:
        return []

    model = get_embedding_model()
    query_embedding = model.encode([query]).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    chunks = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        if dist is None:
            continue
        if dist <= max_distance:
            chunks.append({
                "text": doc,
                "source": meta.get("source", "unknown"),
                "distance": dist
            })

    return chunks


def generate_with_ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 350
        }
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=180) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result.get("response", "").strip()


def answer_with_knowledge(query: str, extra_context: str = "") -> str:
    chunks = retrieve_context(query, top_k=3, max_distance=1.2)

    has_context = len(chunks) > 0

    context_blocks = []
    for chunk in chunks:
        context_blocks.append(
            f"Источник: {chunk['source']}\nТекст: {chunk['text']}"
        )

    retrieved_context = "\n\n".join(context_blocks) if has_context else "Релевантный контекст в базе знаний не найден."

    prompt = f"""
Ты AI-ассистент для самоконтроля диабета.

Отвечай пациенту:
- кратко
- понятно
- спокойно
- безопасно
- без выдуманных ссылок
- без заглушек
- без назначения лечения и дозировок

Главные правила:
- если релевантный контекст найден, опирайся на него в первую очередь
- если релевантный контекст не найден, отвечай осторожно на основе общих знаний
- не выдумывай факты, которых нет ни в контексте, ни в базовых знаниях
- если вопрос про питание, объясняй через углеводы, размер порции, хлебные единицы и контроль сахара
- если вопрос про препараты, используй дополнительный контекст о препаратах
- если вопрос тревожный, советуй измерить сахар и обратиться за медицинской помощью при ухудшении
- не пиши строку "Источники:"
- не упоминай технические детали базы знаний

Дополнительный контекст:
{extra_context if extra_context else "Нет"}

Контекст из базы знаний:
{retrieved_context}

Вопрос пользователя:
{query}
""".strip()

    answer = generate_with_ollama(prompt)
    return answer