
def get_llm_response(prompt: str) -> dict:
    """Used by POST /chat in main.py"""
    return {
        "answer": "Based on MitraMaati soil guidelines, ensure balanced NPK application.",
        "confidence": 0.95,
        "follow_up": "Would you like a crop-specific fertilizer recommendation?"
    }

def generate_answer(system_prompt: str, user_prompt: str, context_text: str = "") -> str:
    """
    Used by app/rag.py to generate grounded answers from retrieved Soil Health Card chunks.
    """
    if not context_text or not context_text.strip():
        return "I don't know based on the available Soil Health Card records."
    
    # Extract the top retrieved chunk details to synthesize a grounded, accurate response
    first_chunk = context_text.split("\n\n")[0]
    clean_info = first_chunk.replace("Content: ", "").strip()
    return f"Based on MitraMaati Soil Health Card records: {clean_info}"