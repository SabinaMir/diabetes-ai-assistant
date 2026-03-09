from pathlib import Path
import statistics

import matplotlib.pyplot as plt

from src.db import get_recent_glucose


HYPO_THRESHOLD = 3.9
TARGET_LOW = 4.0
TARGET_HIGH = 7.8
HIGH_THRESHOLD = 10.0


def analyze_glucose(user_id: str) -> str:
    rows = get_recent_glucose(user_id, limit=30)

    if not rows:
        return "У вас пока нет записей сахара для анализа."

    values = [row[0] for row in rows if row[0] is not None]

    if not values:
        return "Не удалось найти значения сахара для анализа."

    avg_value = statistics.mean(values)
    min_value = min(values)
    max_value = max(values)

    hypo_count = sum(v < HYPO_THRESHOLD for v in values)
    high_count = sum(v > HIGH_THRESHOLD for v in values)

    lines = [
        "📊 Анализ последних измерений сахара",
        "",
        f"Количество записей: {len(values)}",
        f"Средний сахар: {avg_value:.2f} ммоль/л",
        f"Минимум: {min_value:.2f}",
        f"Максимум: {max_value:.2f}",
        "",
    ]

    if avg_value > TARGET_HIGH:
        lines.append("⚠️ Средний уровень сахара выше целевого диапазона.")
    elif avg_value < TARGET_LOW:
        lines.append("⚠️ Средний уровень сахара ниже целевого диапазона.")
    else:
        lines.append("✅ Средний уровень сахара находится в целевом диапазоне.")

    if hypo_count > 0:
        lines.append(f"⚠️ Обнаружено {hypo_count} эпизодов возможной гипогликемии (< {HYPO_THRESHOLD}).")

    if high_count > 0:
        lines.append(f"⚠️ Обнаружено {high_count} эпизодов выраженной гипергликемии (> {HIGH_THRESHOLD}).")

    trend_text = detect_trend(values)
    if trend_text:
        lines.append(trend_text)

    lines.append("")
    lines.append("ℹ️ Это автоматический анализ. Для медицинских решений обязательно консультируйтесь с врачом.")

    return "\n".join(lines)


def detect_trend(values: list[float]) -> str:
    if len(values) < 4:
        return "ℹ️ Пока недостаточно данных, чтобы уверенно оценить тренд."

    chronological = list(reversed(values))

    first_half = chronological[: len(chronological) // 2]
    second_half = chronological[len(chronological) // 2 :]

    if not first_half or not second_half:
        return ""

    first_avg = statistics.mean(first_half)
    second_avg = statistics.mean(second_half)
    diff = second_avg - first_avg

    if diff > 1.0:
        return "📈 Есть тенденция к повышению сахара в последних измерениях."
    if diff < -1.0:
        return "📉 Есть тенденция к снижению сахара в последних измерениях."

    return "➡️ Выраженного тренда к росту или снижению сахара не видно."


def build_glucose_plot(user_id: str) -> str | None:
    rows = get_recent_glucose(user_id, limit=30)

    if not rows:
        return None

    values = [row[0] for row in rows if row[0] is not None]

    if not values:
        return None

    chronological = list(reversed(values))
    x = list(range(1, len(chronological) + 1))

    output_dir = Path("artifacts")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / f"glucose_plot_{user_id}.png"

    plt.figure(figsize=(8, 4.5))
    plt.plot(x, chronological, marker="o")
    plt.axhline(TARGET_LOW, linestyle="--")
    plt.axhline(TARGET_HIGH, linestyle="--")
    plt.axhline(HYPO_THRESHOLD, linestyle=":")
    plt.axhline(HIGH_THRESHOLD, linestyle=":")
    plt.title("Динамика сахара")
    plt.xlabel("Измерение")
    plt.ylabel("ммоль/л")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    return str(output_path)