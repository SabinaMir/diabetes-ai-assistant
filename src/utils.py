import re


def extract_glucose_value(text: str):
    match = re.search(r"(\d+[.,]?\d*)", text)
    if not match:
        return None

    value = match.group(1).replace(",", ".")
    return float(value)