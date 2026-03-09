import gradio as gr

from src.router import route_with_llm
from src.analytics import analyze_glucose, build_glucose_plot
from src.drug_lookup import build_drug_context
from src.rag import build_rag_index, answer_with_knowledge
from src.db import (
    init_db,
    save_glucose,
    get_recent_glucose,
    save_symptom,
    get_recent_symptoms,
)
from src.utils import extract_glucose_value


init_db()
build_rag_index()


def format_glucose_rows(rows):
    if not rows:
        return "У вас пока нет записей сахара."

    lines = ["Последние записи сахара:"]
    for value, note, created_at in rows:
        lines.append(f"- {value} | {note} | {created_at}")

    return "\n".join(lines)


def format_symptom_rows(rows):
    if not rows:
        return "У вас пока нет записей самочувствия."

    lines = ["Последние записи самочувствия:"]
    for symptom, created_at in rows:
        lines.append(f"- {symptom} | {created_at}")

    return "\n".join(lines)


def chat(message, history, user_id):
    if not message or not message.strip():
        return "Введите сообщение.", None

    if not user_id or not user_id.strip():
        return "Пожалуйста, введите user_id перед началом работы.", None

    intent = route_with_llm(message)

    if intent == "log_glucose":
        value = extract_glucose_value(message)
        if value is None:
            return "Не удалось распознать уровень сахара. Напишите, например: сахар 7.5", None

        save_glucose(user_id, value, message)

        if value < 3.9:
            return (
                f"Я записал уровень сахара: {value}.\n\n"
                "⚠️ Это очень низкий сахар. Если есть возможность, сразу примите быстрые углеводы "
                "(например, сок, сахар или глюкозные таблетки) и повторно измерьте сахар через некоторое время. "
                "Если состояние ухудшается, появляется спутанность сознания или человек теряет сознание, "
                "нужно срочно обратиться за медицинской помощью.",
                None,
            )

        if value >= 13.9:
            return (
                f"Я записал уровень сахара: {value}.\n\n"
                "⚠️ Это очень высокий сахар. Если есть возможность, повторно измерьте глюкозу, "
                "пейте воду и оцените самочувствие. Если есть сильная слабость, тошнота, рвота, "
                "боль в животе или спутанность сознания, нужно срочно обратиться за медицинской помощью.",
                None,
            )

        return f"Я записал уровень сахара: {value}", None

    if intent == "show_glucose":
        rows = get_recent_glucose(user_id)
        return format_glucose_rows(rows), None

    if intent == "plot_glucose":
        plot_path = build_glucose_plot(user_id)
        if plot_path is None:
            return "У вас пока нет записей сахара для построения графика.", None

        return "Вот график ваших последних измерений сахара.", plot_path

    if intent == "log_symptom":
        save_symptom(user_id, message)
        return "Я записал ваше самочувствие.", None

    if intent == "show_symptoms":
        rows = get_recent_symptoms(user_id)
        return format_symptom_rows(rows), None

    if intent == "analyze_glucose":
        return analyze_glucose(user_id), None

    if intent == "emergency":
        emergency_answer = """
Это может быть опасное состояние. Если есть возможность, сначала измерьте сахар.

Такие симптомы, как дрожь, тошнота, сильная слабость, головокружение или спутанность сознания, могут быть связаны как с низким, так и с высоким уровнем глюкозы.

Если состояние ухудшается, появляется рвота, потеря сознания или сахар очень низкий / очень высокий, нужно срочно обратиться за медицинской помощью.
""".strip()
        return emergency_answer, None

    extra_context = build_drug_context(message)
    answer = answer_with_knowledge(message, extra_context=extra_context)

    return answer, None


with gr.Blocks() as demo:
    gr.Markdown("# Diabetes Assistant")
    gr.Markdown("AI-ассистент для дневника сахара, вопросов о диабете и информации о препаратах.")

    user_id = gr.Textbox(label="User ID", placeholder="Например: sabina")

    with gr.Accordion("Что умеет бот", open=False):
        gr.Markdown("""
- записывать сахар в дневник
- записывать симптомы
- показывать историю сахара и самочувствия
- строить график сахара
- анализировать последние измерения
- отвечать на вопросы о диабете
- подсказывать информацию о препаратах и аналогах
""")

    gr.Markdown("**Быстрый старт:** выбери пример или напиши свой вопрос.")

    chatbot = gr.Chatbot(height=420)
    msg = gr.Textbox(label="Сообщение", placeholder="Например: запиши сахар 7.2 после ужина")
    send_btn = gr.Button("Отправить")

    with gr.Row():
        ex1 = gr.Button("запиши сахар 7.2 после ужина")
        ex2 = gr.Button("покажи график сахара")
        ex3 = gr.Button("что такое диабет 2 типа")
        ex4 = gr.Button("аналог оземпика")

    plot_output = gr.Image(label="График сахара")

    def respond(message, history, user_id):
        history = history or []

        if not message or not message.strip():
            return history, "", None

        bot_reply, plot_path = chat(message, history, user_id)

        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": bot_reply})

        return history, "", plot_path

    ex1.click(lambda: "запиши сахар 7.2 после ужина", outputs=msg)
    ex2.click(lambda: "покажи график сахара", outputs=msg)
    ex3.click(lambda: "что такое диабет 2 типа", outputs=msg)
    ex4.click(lambda: "аналог оземпика", outputs=msg)

    send_btn.click(
        respond,
        inputs=[msg, chatbot, user_id],
        outputs=[chatbot, msg, plot_output]
    )

    msg.submit(
        respond,
        inputs=[msg, chatbot, user_id],
        outputs=[chatbot, msg, plot_output]
    )


if __name__ == "__main__":
    demo.launch()