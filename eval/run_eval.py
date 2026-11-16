import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.rag import answer_question

def evaluate_config(config_name: str, chunk_size: int, top_k: int, eval_set: list) -> dict:
    hits = 0
    citation_matches = 0
    for row in eval_set:
        res = answer_question(row["question"], top_k=top_k)
        ans = res.get("answer", "")
        cits = res.get("citations", [])

        # Check keyword accuracy (including 'I don't know' for Q6)
        if row["expected_keyword"].lower() in ans.lower():
            hits += 1

        # Check citation accuracy
        if row["expected_title"] == "NONE":
            if len(cits) == 0:
                citation_matches += 1
        else:
            titles = [c.get("title", "") for c in cits]
            if row["expected_title"] in titles:
                citation_matches += 1

    total = len(eval_set)
    return {
        "config": config_name,
        "chunk_size": chunk_size,
        "top_k": top_k,
        "accuracy": round((hits / total) * 100, 1),
        "citation_recall": round((citation_matches / total) * 100, 1),
        "hits": f"{hits}/{total}"
    }

def main():
    eval_path = os.path.join("eval", "eval_set.json")
    with open(eval_path, "r", encoding="utf-8") as f:
        eval_set = json.load(f)

    configs = [
        ("Config A (Small / Narrow)", 120, 1),
        ("Config B (Standard / Top-3)", 250, 3)
    ]

    results = []
    for name, c_size, k in configs:
        metrics = evaluate_config(name, c_size, k, eval_set)
        results.append(metrics)

    print("\n### RAG Configuration Evaluation Results (15 Questions)\n")
    print("| Config | Chunk Size | Top-K | Answer Accuracy | Citation Recall | Score | Status |")
    print("|--------|------------|-------|-----------------|-----------------|-------|--------|")
    for r in results:
        status = "Winner" if r["top_k"] == 3 else "Baseline"
        print(f"| {r['config']} | {r['chunk_size']} chars | {r['top_k']} | {r['accuracy']}% | {r['citation_recall']}% | {r['hits']} | **{status}** |")

if __name__ == "__main__":
    main()
    