import csv
from src.router import route_with_llm


def main():
    total = 0
    correct = 0

    with open("tests/router_eval.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            question = row["question"]
            expected = row["expected_intent"]
            predicted = route_with_llm(question)

            total += 1
            is_correct = predicted == expected
            if is_correct:
                correct += 1

            print(f"Q: {question}")
            print(f"expected={expected} predicted={predicted} correct={is_correct}")
            print("-" * 40)

    accuracy = correct / total if total else 0
    print(f"Router accuracy: {accuracy:.2%}")


if __name__ == "__main__":
    main()