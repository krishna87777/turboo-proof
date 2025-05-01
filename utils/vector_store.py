from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.texts = []
        self.embeddings = []
        self.index = None

    def add_documents(self, docs):
        for doc in docs:
            content = doc.get("readme") or doc.get("summary") or doc.get("description", "")
            if content:
                self.texts.append(doc)
                self.embeddings.append(self.model.encode(content))

        if self.embeddings:
            self.index = faiss.IndexFlatL2(len(self.embeddings[0]))
            self.index.add(np.array(self.embeddings))

    def search(self, query, k=3):
        if not self.index:
            return []

        query_vec = self.model.encode(query).reshape(1, -1)
        distances, indices = self.index.search(query_vec, k)
        return [self.texts[i] for i in indices[0]]
