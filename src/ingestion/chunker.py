import re
from dataclasses import dataclass
from typing import Any
from src.config import MIN_CHUNK_CHARS, MAX_CHUNK_CHARS
from src.document_metadata import DOCUMENT_METADATA
from src.ingestion.loader import Block

@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    section_heading: str
    heading_path: list[str]
    text: str
    block_types: list[str]
    ordinal_range: tuple[int, int]
    char_count: int
    metadata: dict[str, Any]

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def chunk_document(blocks: list[Block]) -> list[Chunk]:
    if not blocks:
        return []
        
    doc_blocks: dict[str, list[Block]] = {}
    for b in blocks:
        doc_blocks.setdefault(b.document_id, []).append(b)
        
    all_chunks: list[Chunk] = []
    
    for doc_id, b_list in doc_blocks.items():
        # 1. Sort blocks by ordinal
        b_list.sort(key=lambda x: x.ordinal)
        
        doc_meta = DOCUMENT_METADATA.get(doc_id, {
            "title": doc_id,
            "publisher": "Unknown",
            "year": 1970,
            "url": ""
        })
        
        raw_chunks = []
        current_chunk_blocks = []
        
        def flush_chunk():
            nonlocal current_chunk_blocks
            if not current_chunk_blocks:
                return
            
            types = [b.type for b in current_chunk_blocks]
            text = "\n\n".join(b.text for b in current_chunk_blocks)
            heading_path = current_chunk_blocks[0].heading_path
            section_heading = heading_path[-1] if heading_path else "Unknown Section"
            
            raw_chunks.append({
                "document_id": doc_id,
                "section_heading": section_heading,
                "heading_path": heading_path,
                "text": text,
                "block_types": types,
                "ordinal_range": (current_chunk_blocks[0].ordinal, current_chunk_blocks[-1].ordinal),
                "char_count": len(text)
            })
            current_chunk_blocks = []

        # 2. Walk blocks
        for b in b_list:
            if b.type == "heading":
                is_level_1 = (b.level == 1)
                current_text_len = sum(len(cb.text) for cb in current_chunk_blocks)
                current_chars = current_text_len + max(0, (len(current_chunk_blocks) - 1) * 2)
                
                if is_level_1 or current_chars >= MIN_CHUNK_CHARS:
                    flush_chunk()
                current_chunk_blocks.append(b)
            elif b.type == "table":
                flush_chunk()
                current_chunk_blocks.append(b)
                flush_chunk()
            else:
                current_chunk_blocks.append(b)
                
        # 3. Flush remaining buffer
        flush_chunk()
        
        # 4. Merge pass
        merged_chunks = []
        i = 0
        while i < len(raw_chunks):
            chunk_data = raw_chunks[i]
            is_table = "table" in chunk_data["block_types"]
            
            if chunk_data["char_count"] < MIN_CHUNK_CHARS and i + 1 < len(raw_chunks) and not is_table:
                next_chunk = raw_chunks[i+1]
                next_is_table = "table" in next_chunk["block_types"]
                if not next_is_table:
                    # merge into next chunk
                    next_chunk["text"] = chunk_data["text"] + "\n\n" + next_chunk["text"]
                    next_chunk["block_types"] = chunk_data["block_types"] + next_chunk["block_types"]
                    next_chunk["ordinal_range"] = (chunk_data["ordinal_range"][0], next_chunk["ordinal_range"][1])
                    next_chunk["char_count"] = len(next_chunk["text"])
                else:
                    merged_chunks.append(chunk_data)
            else:
                merged_chunks.append(chunk_data)
            i += 1
            
        # 5. Split pass
        split_chunks = []
        for chunk_data in merged_chunks:
            if chunk_data["char_count"] > MAX_CHUNK_CHARS and "table" not in chunk_data["block_types"]:
                paragraphs = chunk_data["text"].split("\n\n")
                current_text = ""
                for p in paragraphs:
                    if len(current_text) + len(p) + 2 > MAX_CHUNK_CHARS and current_text:
                        split_chunks.append({
                            **chunk_data,
                            "text": current_text,
                            "char_count": len(current_text)
                        })
                        current_text = p
                    else:
                        if current_text:
                            current_text += "\n\n" + p
                        else:
                            current_text = p
                if current_text:
                    split_chunks.append({
                        **chunk_data,
                        "text": current_text,
                        "char_count": len(current_text)
                    })
            else:
                split_chunks.append(chunk_data)
                
        # 6. Assign chunk_id
        seq = 1
        for chunk_data in split_chunks:
            slug = slugify(chunk_data["section_heading"])
            chunk_id = f"{doc_id}__{slug}__{seq:03d}"
            
            all_chunks.append(Chunk(
                chunk_id=chunk_id,
                document_id=doc_id,
                section_heading=chunk_data["section_heading"],
                heading_path=chunk_data["heading_path"],
                text=chunk_data["text"],
                block_types=chunk_data["block_types"],
                ordinal_range=chunk_data["ordinal_range"],
                char_count=chunk_data["char_count"],
                metadata=doc_meta.copy()
            ))
            seq += 1
            
    return all_chunks
