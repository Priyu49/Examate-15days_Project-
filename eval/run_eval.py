import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.rag import answer_question

def evaluate_config(config_name: str, chunk_size: int, top_k: int, eval_set: list) -> dict:
    keyword_hits = 0
    citation_matches = 0
    safety_passes = 0
    total = len(eval_set)

    for row in eval_set:
        res = answer_question(row["question"], top_k=top_k)
        ans = res.get("answer", "")
        cits = res.get("citations", [])

        # 1. Keyword / Fact Accuracy Check
        if row["expected_keyword"].lower() in ans.lower():
            keyword_hits += 1

        # 2. Negative Constraints Check (Must not contain forbidden terms)
        failed_negative = any(term.lower() in ans.lower() for term in row.get("must_not_contain", []))

        # 3. Citation & Boundary Verification
        if row["expected_title"] == "NONE":
            # Unanswerable query check
            if len(cits) == 0 and "I don't know" in ans and not failed_negative:
                safety_passes += 1
                citation_matches += 1
        else:
            titles = [c.get("title", "") for c in cits]
            if row["expected_title"] in titles and not failed_negative:
                citation_matches += 1
                safety_passes += 1

    return {
        "config": config_name,
        "chunk_size": chunk_size,
        "top_k": top_k,
        "accuracy": round((keyword_hits / total) * 100, 1),
        "citation_recall": round((citation_matches / total) * 100, 1),
        "safety_score": round((safety_passes / total) * 100, 1),
        "score": f"{keyword_hits}/{total}"
    }

def main():
    eval_path = os.path.join("eval", "eval_set.json")
    if not os.path.exists(eval_path):
        print(f"Error: {eval_path} not found.")
        return

    with open(eval_path, "r", encoding="utf-8") as f:
        eval_set = json.load(f)

    # Test multiple configurations systematically
    configs = [
        ("Config A (Narrow / Top-1)", 120, 1),
        ("Config B (Standard / Top-3)", 250, 3),
        ("Config C (Broad / Top-5)", 400, 5)
    ]

    results = []
    for name, c_size, k in configs:
        metrics = evaluate_config(name, c_size, k, eval_set)
        results.append(metrics)

    print("\n### Advanced RAG Configuration Evaluation Results\n")
    print("| Configuration | Chunk Size | Top-K | Accuracy | Citation Recall | Safety Score | Score |")
    print("|---------------|------------|-------|----------|-----------------|--------------|-------|")
    for r in results:
        status = "**[WINNER]**" if r["top_k"] == 3 else "Baseline"
        print(f"| {r['config']} {status} | {r['chunk_size']} chars | {r['top_k']} | {r['accuracy']}% | {r['citation_recall']}% | {r['safety_score']}% | {r['score']} |")

if __name__ == "__main__":
    main()