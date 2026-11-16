from app.chunking import chunk_records
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class SimpleVectorStore:
    def __init__(self):
        self.chunks = chunk_records()
        self.texts = [c["text"] for c in self.chunks]

    def similarity_search(self, query: str, top_k: int = 3):
        if not self.texts:
            return []
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(self.texts)
        try:
            query_vec = vectorizer.transform([query])
            scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
            top_indices = np.argsort(scores)[::-1][:top_k]
            results = []
            for idx in top_indices:
                if scores[idx] > 0.0:
                    res = self.chunks[idx].copy()
                    res["score"] = float(scores[idx])
                    results.append(res)
            return results
        except Exception:
            return self.chunks[:top_k]

vector_store = SimpleVectorStore()