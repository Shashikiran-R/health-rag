import pytest
from src.ingestion.loader import Block
from src.ingestion.chunker import chunk_document, Chunk

def test_heading_starts_new_chunk():
    blocks = [
        Block(document_id="doc1", ordinal=1, type="heading", text="H1", heading_path=["H1"], level=1),
        Block(document_id="doc1", ordinal=2, type="paragraph", text="A"*150, heading_path=["H1"]),
        Block(document_id="doc1", ordinal=3, type="heading", text="H2", heading_path=["H1", "H2"], level=1),
        Block(document_id="doc1", ordinal=4, type="paragraph", text="B"*150, heading_path=["H1", "H2"]),
    ]
    chunks = chunk_document(blocks)
    assert len(chunks) == 2
    assert "H1" in chunks[0].text
    assert "H2" in chunks[1].text

def test_table_stays_intact():
    blocks = [
        Block(document_id="doc1", ordinal=1, type="paragraph", text="A"*150, heading_path=["H1"]),
        Block(document_id="doc1", ordinal=2, type="table", text="T"*1600, heading_path=["H1"]),
        Block(document_id="doc1", ordinal=3, type="paragraph", text="B"*150, heading_path=["H1"]),
    ]
    chunks = chunk_document(blocks)
    table_chunk = next(c for c in chunks if "table" in c.block_types)
    assert len(table_chunk.text) == 1600
    assert table_chunk.char_count == 1600

def test_small_chunks_merged():
    blocks = [
        Block(document_id="doc1", ordinal=1, type="heading", text="H1", heading_path=["H1"], level=1),
        Block(document_id="doc1", ordinal=2, type="paragraph", text="S", heading_path=["H1"]),
        Block(document_id="doc1", ordinal=3, type="heading", text="H2", heading_path=["H2"], level=1),
        Block(document_id="doc1", ordinal=4, type="paragraph", text="B"*150, heading_path=["H2"]),
    ]
    chunks = chunk_document(blocks)
    assert len(chunks) == 1
    assert "H1" in chunks[0].text
    assert "H2" in chunks[0].text

def test_large_chunks_split():
    blocks = [
        Block(document_id="doc1", ordinal=1, type="heading", text="H1", heading_path=["H1"], level=1),
        Block(document_id="doc1", ordinal=2, type="paragraph", text="A"*800, heading_path=["H1"]),
        Block(document_id="doc1", ordinal=3, type="paragraph", text="B"*800, heading_path=["H1"]),
    ]
    chunks = chunk_document(blocks)
    assert len(chunks) == 2
    assert chunks[0].char_count <= 1500
    assert chunks[1].char_count <= 1500

def test_metadata_attached():
    blocks = [
        Block(document_id="cold-food-storage", ordinal=1, type="paragraph", text="A"*150, heading_path=[])
    ]
    chunks = chunk_document(blocks)
    assert chunks[0].metadata["publisher"] == "USDA / FoodSafety.gov"
    assert chunks[0].metadata["year"] == 2023
    assert chunks[0].metadata["url"] == "https://www.foodsafety.gov/food-safety-charts/cold-food-storage-charts"

def test_all_blocks_consumed():
    blocks = [
        Block(document_id="doc1", ordinal=1, type="heading", text="H1", heading_path=["H1"], level=1),
        Block(document_id="doc1", ordinal=2, type="paragraph", text="P1", heading_path=["H1"]),
        Block(document_id="doc1", ordinal=3, type="table", text="T1", heading_path=["H1"]),
    ]
    chunks = chunk_document(blocks)
    combined_text = "\n\n".join(c.text for c in chunks)
    assert "H1" in combined_text
    assert "P1" in combined_text
    assert "T1" in combined_text
