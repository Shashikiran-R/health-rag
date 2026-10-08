from typing import Any, Dict, List
from src.document_metadata import DOCUMENT_METADATA

class PromptBuilder:
    def build(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        prompt = """You are a dietary guidance assistant. You answer ONLY from the provided
source chunks. You NEVER use your own knowledge.

RULES:
1. Every claim must include a citation: [Document Title, Publisher, Year](URL)
2. If multiple documents address the question, answer from EACH document
   separately with its own citation. Never blend sources.
3. If the chunks don't contain the answer, say so and list the documents
   you searched.
4. Keep answers at the population level. Never make personal recommendations.
5. Never provide calorie targets, weight targets, or medical advice.

CHUNKS:
"""
        doc_ids_searched = set()
        
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            doc_id = metadata.get("document_id")
            if doc_id:
                doc_ids_searched.add(doc_id)
            
            doc_meta = DOCUMENT_METADATA.get(doc_id, {})
            title = doc_meta.get("title", doc_id)
            publisher = metadata.get("publisher", doc_meta.get("publisher", ""))
            year = metadata.get("year", doc_meta.get("year", ""))
            url = metadata.get("url", doc_meta.get("url", ""))
            section_heading = metadata.get("section_heading", "Unknown Section")
            text = chunk.get("text", "")
            
            prompt += f"---\n[Source: {title} ({publisher}, {year})]\nSection: {section_heading}\n{text}\nURL: {url}\n"
        
        # If no chunks provided, list the documents in the corpus
        if not chunks:
            doc_ids_searched = set(DOCUMENT_METADATA.keys())
            
        doc_list = ", ".join([DOCUMENT_METADATA.get(did, {}).get("title", did) for did in doc_ids_searched])
        prompt += f"---\nSearched Documents: {doc_list}\n"
        prompt += f"\nUSER QUESTION:\n{query}"
        
        return prompt
