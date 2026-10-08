from typing import Any, Dict, List
from src.config import RELEVANCE_THRESHOLD

class RelevanceChecker:
    def check_relevance(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter results below RELEVANCE_THRESHOLD (or SIMILARITY_THRESHOLD).
        
        Note: ChromaDB with SentenceTransformers (cosine/L2) returns distances.
        Smaller distance means more similar.
        If using cosine distance, similarity = 1 - distance.
        So similarity >= THRESHOLD is equivalent to distance <= (1 - THRESHOLD).
        Wait, ChromaDB typically returns L2 or cosine distance.
        The architecture says: "Filter results below SIMILARITY_THRESHOLD; return empty list if none pass"
        And "Score threshold: 0.3. Chunks below this are treated as irrelevant."
        Actually, chroma returns distances. Let's assume similarity = 1 - distance.
        """
        if not results or not results.get("distances"):
            return []
            
        relevant_chunks = []
        distances = results["distances"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        
        for i in range(len(distances)):
            distance = distances[i]
            # Assuming cosine distance: similarity = 1 - distance
            # If distance is < 0.7, similarity > 0.3. 
            # Or if it's already a similarity score, score >= 0.3.
            # We'll use distance <= (1 - RELEVANCE_THRESHOLD) assuming cosine distance.
            # But wait, we can just return anything where (1 - distance) >= RELEVANCE_THRESHOLD.
            similarity = 1.0 - distance
            if similarity >= RELEVANCE_THRESHOLD:
                relevant_chunks.append({
                    "text": documents[i],
                    "metadata": metadatas[i],
                    "score": similarity
                })
                
        return relevant_chunks
