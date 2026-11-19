from app.tools import classify_soil_card, parse_soil_query
from app.vectorstore import vector_store


def run_agent_loop(query: str) -> dict:
    """
    Hand-written agent: calls classify_soil_card when the question contains a
    soil parameter and a number (e.g. 'classify nitrogen 200'), otherwise
    answers from RAG semantic search.
    """
    parsed = parse_soil_query(query)
    if parsed:
        name, value = parsed
        result = classify_soil_card(name, value)
        return {
            "agent_type": "tool_execution",
            "tool_output": result,
            "answer": (
                f"{result['parameter']} = {result['measured_value']} {result.get('unit', '')}: "
                f"{result['recommendation']}"
            ),
            "citations": [{"title": result["parameter"], "page": result.get("page", 1),
                           "source": result.get("source_url", "")}],
        }

    hits = vector_store.similarity_search(query, top_k=2)
    if hits:
        top = hits[0]
        answer = f"According to Soil Health guidelines ({top['title']}): {top['text']}"
        citations = [{"title": top["title"], "page": top["page"], "source": top["source"]}]
    else:
        answer = "I don't know based on available Soil Health Card records."
        citations = []

    return {"agent_type": "rag_search", "answer": answer, "citations": citations, "tool_output": None}
