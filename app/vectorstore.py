import os
import chromadb
from app.chunking import chunk_records
from app.embed import embed_texts, embed_query

CHROMA_DIR = os.path.join("data", "chroma_db")
COLLECTION_NAME = "mitramaati_shc_chunks"

class ChromaVectorStore:
    def __init__(self, persist_directory: str = CHROMA_DIR):
        os.makedirs(persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        self.chunks = chunk_records()
        self._index_chunks()

    def _index_chunks(self):
        if not self.chunks:
            return
        ids = [c["id"] for c in self.chunks]
        texts = [c["text"] for c in self.chunks]
        metadatas = [
            {
                "id": c["id"],
                "source": str(c.get("source", "https://soilhealth.dac.gov.in/files/FAQ_Final_English.pdf")),
                "page": int(c.get("page", 1)),
                "title": str(c.get("title", "Soil Parameter"))
            }
            for c in self.chunks
        ]
        embeddings = embed_texts(texts)
        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def similarity_search(self, query: str, top_k: int = 3) -> list[dict]:
        if not query or not query.strip() or not self.chunks:
            return []

        query_embedding = embed_query(query)
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, len(self.chunks)),
            include=["documents", "metadatas", "distances"]
        )

        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        hits = []
        for doc, meta, dist in zip(docs, metas, distances):
            # Cosine similarity = 1 - cosine distance
            similarity = max(0.0, round(1.0 - float(dist), 4))
            hits.append({
                "id": meta.get("id", "chunk_1"),
                "source": meta.get("source", "https://soilhealth.dac.gov.in/files/FAQ_Final_English.pdf"),
                "page": meta.get("page", 1),
                "title": meta.get("title", "Soil Parameter"),
                "text": doc,
                "score": similarity
            })
        return hits

vector_store = ChromaVectorStore()