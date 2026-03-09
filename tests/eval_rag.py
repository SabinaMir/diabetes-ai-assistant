import csv
from src.rag import retrieve_context


def main():
    total = 0
    correct = 0

    with open("tests/rag_eval.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            question = row["question"]
            expected_source = row["expected_source"]

            chunks = retrieve_context(question, top_k=2)
            sources = [chunk["source"] for chunk in chunks]

            hit = any(expected_source in source for source in sources)

            total += 1
            if hit:
                correct += 1

            print(f"Q: {question}")
            print(f"sources={sources}")
            print(f"hit={hit}")
            print("-" * 40)

    hit_rate = correct / total if total else 0
    print(f"RAG retrieval hit@2: {hit_rate:.2%}")


if __name__ == "__main__":
    main()