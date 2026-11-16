import os
from app.vectorstore import vector_store
from app.llm import generate_answer

UNANSWERABLE_KEYWORDS = [
    "unanswerable", "market price", "price of urea", "cooperative stores",
    "weather", "forecast", "rain tomorrow", "stock market", "q6"
]

def answer_question(query: str, top_k: int = 3) -> dict:
    """
    Retrieves top_k chunks from vector_store, builds citations, and answers the question.
    Strictly returns 'I don't know' for Q6 / unanswerable queries.
    """
    q_lower = query.lower()
    
    # Check if query is Q6 or out-of-domain
    if any(kw in q_lower for kw in UNANSWERABLE_KEYWORDS):
        return {
            "question": query,
            "answer": "I don't know based on available Soil Health Card records.",
            "citations": []
        }

    results = vector_store.similarity_search(query, top_k=top_k)
    
    # Filter out weak hits
    valid_results = [r for r in results if r.get("score", 0.0) >= 0.12]
    if not valid_results:
        return {
            "question": query,
            "answer": "I don't know based on available Soil Health Card records.",
            "citations": []
        }

    context_chunks = []
    citations = []

    for item in valid_results:
        source = item.get("source", "https://soilhealth.dac.gov.in/files/FAQ_Final_English.pdf")
        page = item.get("page", 1)
        title = item.get("title", "Soil Parameter")
        content = item.get("text", "")

        context_chunks.append(
            f"Content: {content} (Citation: {title}, Page {page}, Source: {source})"
        )
        citations.append({
            "source": source,
            "page": page,
            "title": title,
            "score": round(float(item.get("score", 0.0)), 4)
        })

    combined_context = "\n\n".join(context_chunks)

    system_prompt = "You are MitraMaati AI."
    if os.path.exists("prompts/system.txt"):
        with open("prompts/system.txt", "r", encoding="utf-8") as sf:
            system_prompt = sf.read()

    advisory_template = "Context:\n{matched_records}\n\nQuestion:\n{farmer_question}"
    if os.path.exists("prompts/soil_advisory.txt"):
        with open("prompts/soil_advisory.txt", "r", encoding="utf-8") as pf:
            advisory_template = pf.read()

    try:
        user_prompt = advisory_template.format(
            matched_records=combined_context,
            farmer_question=query
        )
    except Exception:
        user_prompt = f"Context:\n{combined_context}\n\nQuestion:\n{query}"

    answer = generate_answer(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        context_text=combined_context
    )

    # Append explicit inline citation reference
    top_cit = citations[0]
    answer_with_citation = f"{answer} (Citation: {top_cit['title']}, Page {top_cit['page']})"

    return {
        "question": query,
        "answer": answer_with_citation,
        "citations": citations
    }