from app.tools import classify_soil_card
from app.vectorstore import vector_store

def run_agent_loop(query: str) -> dict:
    """
    A hand-written agent that can call RAG semantic search or classify_soil_card tool.
    """
    q_lower = query.lower()
    
    # Check if user is asking to classify a specific soil parameter value
    if "classify" in q_lower or "test" in q_lower or "value" in q_lower:
        # Simple extraction heuristic for testing tool execution
        if "nitrogen" in q_lower:
            result = classify_soil_card("Nitrogen (N)", 200.0)
        elif "phosphorus" in q_lower:
            result = classify_soil_card("Phosphorus (P)", 8.0)
        elif "ph" in q_lower:
            result = classify_soil_card("Soil pH", 5.5)
        else:
            result = classify_soil_card("Organic Carbon (OC)", 0.5)
        
        return {
            "agent_type": "tool_execution",
            "tool_output": result,
            "answer": f"Analyzed {result['parameter']} with measured value {result['measured_value']} {result.get('unit','')}: {result['recommendation']}"
        }
    else:
        # Default to RAG vector search
        hits = vector_store.similarity_search(query, top_k=2)
        if hits:
            top = hits[0]
            answer = f"According to Soil Health guidelines ({top['title']}): {top['text']}"
            citations = [{"title": top["title"], "page": top["page"], "source": top["source"]}]
        else:
            answer = "I don't know based on available Soil Health Card records."
            citations = []

        return {
            "agent_type": "rag_search",
            "answer": answer,
            "citations": citations
        }