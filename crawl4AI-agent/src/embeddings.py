import torch
from sentence_transformers import SentenceTransformer
from typing import List

class EmbeddingGenerator:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def generate_embedding(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.model.get_sentence_embedding_dimension()
        
        embedding = self.model.encode(text)
        return embedding.tolist()

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        import numpy as np
        
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

embedding_generator = EmbeddingGenerator()