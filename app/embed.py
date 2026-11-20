MODEL_NAME = "all-MiniLM-L6-v2"
_model = None

def get_embedding_model():
    """Loads and caches the sentence-transformers all-MiniLM-L6-v2 model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(MODEL_NAME)
    return _model

def embed_texts(texts: list[str]) -> list[list[float]]:
    """Encodes a list of strings into normalized dense vectors using all-MiniLM-L6-v2."""
    if not texts:
        return []
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return embeddings.tolist()

def embed_query(query: str) -> list[float]:
    """Encodes a single search query into a normalized dense vector."""
    return embed_texts([query])[0]

def get_embeddings(texts: list[str]):
    """Backwards-compatible helper returning the model and dense embedding vectors."""
    model = get_embedding_model()
    vectors = embed_texts(texts)
    return model, vectors
