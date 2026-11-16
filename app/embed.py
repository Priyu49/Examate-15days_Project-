from sklearn.feature_extraction.text import TfidfVectorizer

def get_embeddings(texts: list[str]):
    # Lightweight robust embedding/vectorizer proxy compatible with environment
    vectorizer = TfidfVectorizer(stop_words='english')
    matrix = vectorizer.fit_transform(texts)
    return vectorizer, matrix