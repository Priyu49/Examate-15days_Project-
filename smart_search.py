import os
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def smart_search(query: str):
    path = os.path.join("data", "records.json")
    if not os.path.exists(path):
        return []
    
    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)
        
    if not query.strip():
        return records

    # Fallback substring matching if query is too short or numeric
    if len(query.strip()) < 3 or query.strip().isdigit():
        results = [
            r for r in records if 
            query.lower() in str(r.get("sample_id", "")).lower() or
            query.lower() in str(r.get("parameter_name", "")).lower() or
            query.lower() in str(r.get("what_it_means", "")).lower()
        ]
        return results if results else records[:3]

    try:
        texts = [f"{r.get('parameter_name', '')} {r.get('what_it_means', '')}" for r in records]
        
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(texts)
        query_vec = vectorizer.transform([query])
        
        similarity_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
        ranked_indices = np.argsort(similarity_scores)[::-1]
        
        ranked_records = [records[i] for i in ranked_indices if similarity_scores[i] > 0.0]
        return ranked_records if ranked_records else records[:3]
    except Exception:
        return [r for r in records if query.lower() in str(r).lower()]