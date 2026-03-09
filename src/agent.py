from src.rag import rag_answer
from src.llm import llm_generate
from src.glucose_diary import (
    log_glucose,
    show_glucose_records
)

from src.symptom_diary import (
    log_symptom,
    show_symptom_records
)

from src.drug_lookup import find_drug, find_analogs


# ---------------------------------------------------
# INTENT DETECTION
# ---------------------------------------------------

def detect_intent(message: str):

    text = message.lower()

    if "покажи мой сахар" in text or "мои записи сахара" in text:
        return "show_glucose"

    if "покажи симптомы" in text or "мое самочувствие" in text or "мои симптомы" in text:
        return "show_symptoms"

    if "самочувствие" in text or "симптом" in text or "слабость" in text or "тошнота" in text:
        return "log_symptom"

    if "сахар" in text:
        return "log_glucose"

    if "аналог" in text:
        return "drug_analogs"

    if "метформин" in text or "форсига" in text or "инсулин" in text or "препарат" in text or "лекарство" in text:
        return "drug_info"

    if "можно ли" in text or "есть" in text or "банан" in text:
        return "nutrition_question"

    if "диабет" in text:
        return "education"

    return "general_qa"


# ---------------------------------------------------
# AGENT MAIN FUNCTION
# ---------------------------------------------------

def agent(message: str, user_id="default_user"):

    intent = detect_intent(message)

    # -------------------------------
    # LOG GLUCOSE
    # -------------------------------

    if intent == "log_glucose":

        value = extract_glucose_value(message)

        if value:
            log_glucose(user_id, value, message)
            return f"Я записал уровень сахара: {value}"

        return "Я не смог понять уровень сахара."


    # -------------------------------
    # SHOW GLUCOSE
    # -------------------------------

    if intent == "show_glucose":

        records = show_glucose_records(user_id)

        if not records:
            return "У вас пока нет записей сахара."

        text = "Последние записи сахара:\n"

        for r in records:
            text += f"- {r['value']} | {r['note']} | {r['timestamp']}\n"

        return text


    # -------------------------------
    # LOG SYMPTOM
    # -------------------------------

    if intent == "log_symptom":

        log_symptom(user_id, message)

        return "Я записал ваше самочувствие."


    # -------------------------------
    # SHOW SYMPTOMS
    # -------------------------------

    if intent == "show_symptoms":

        records = show_symptom_records(user_id)

        if not records:
            return "У вас пока нет записей симптомов."

        text = "Последние записи самочувствия:\n"

        for r in records:
            text += f"- {r['note']} | {r['timestamp']}\n"

        return text


    # -------------------------------
    # DRUG INFO
    # -------------------------------

    if intent == "drug_info":

        drug = find_drug(message)

        if drug:

            prompt = f"""
Объясни пациенту простыми словами препарат для лечения диабета.

Название: {drug['brand_name']}
Действующее вещество: {drug['inn']}
Класс: {drug['drug_class']}

Ответ должен быть коротким и понятным.
"""

            return llm_generate(prompt)

        return "Я не нашёл этот препарат в базе."


    # -------------------------------
    # DRUG ANALOGS
    # -------------------------------

    if intent == "drug_analogs":

        inn, analogs = find_analogs(message)

        if analogs:

            analog_text = ", ".join(analogs)

            prompt = f"""
Объясни пациенту аналоги лекарства.

Действующее вещество: {inn}
Аналоги: {analog_text}

Ответь понятно.
"""

            return llm_generate(prompt)

        return "Я не нашёл аналоги этого препарата."


    # -------------------------------
    # RAG EDUCATION
    # -------------------------------

    if intent == "education":

        answer, sources = rag_answer(message)

        return f"[RAG] {answer}\n\nИсточники: {', '.join(sources)}"


    # -------------------------------
    # GENERAL LLM
    # -------------------------------

    return llm_generate(message)


# ---------------------------------------------------
# HELPERS
# ---------------------------------------------------

def extract_glucose_value(text):

    import re

    match = re.search(r"\d+(\.\d+)?", text)

    if match:
        return float(match.group())

    return None