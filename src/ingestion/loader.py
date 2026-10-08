import json
from dataclasses import dataclass
from typing import Optional

@dataclass
class Block:
    document_id: str
    ordinal: int
    type: str
    text: str
    heading_path: list[str]
    level: Optional[int] = None

def load_blocks(path: str) -> list[Block]:
    blocks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            blocks.append(Block(
                document_id=data.get("document_id", ""),
                ordinal=data.get("ordinal", 0),
                type=data.get("type", ""),
                text=data.get("text", ""),
                heading_path=data.get("heading_path", []),
                level=data.get("level")
            ))
    return blocks
