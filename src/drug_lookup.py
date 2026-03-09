import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "drugs" / "diabetes_drugs_ru.csv"

df = pd.read_csv(CSV_PATH, encoding="utf-8")


def find_drug(query: str):
    query = query.lower()

    for _, row in df.iterrows():
        brand = str(row["brand_name"]).lower()
        inn = str(row["inn"]).lower()

        if brand in query or inn in query:
            return row.to_dict()

    return None


def find_analogs(query: str):
    query = query.lower()

    for _, row in df.iterrows():
        brand = str(row["brand_name"]).lower()
        inn = str(row["inn"])

        if brand in query:
            analogs = df[df["inn"] == inn]["brand_name"].tolist()
            return {
                "brand_name": row["brand_name"],
                "inn": inn,
                "drug_class": row["drug_class"],
                "analogs": analogs,
            }

    return None


def build_drug_context(query: str) -> str:
    drug = find_drug(query)
    analogs = find_analogs(query)

    blocks = []

    if drug:
        blocks.append(
            f"Препарат: {drug['brand_name']}\n"
            f"Действующее вещество: {drug['inn']}\n"
            f"Класс: {drug['drug_class']}"
        )

    if analogs:
        blocks.append(
            f"Исходный препарат: {analogs['brand_name']}\n"
            f"Действующее вещество: {analogs['inn']}\n"
            f"Класс: {analogs['drug_class']}\n"
            f"Аналоги по действующему веществу: {', '.join(analogs['analogs'])}"
        )

    return "\n\n".join(blocks)