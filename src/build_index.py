import os
import json
import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = os.path.join("data", "chunks.json")
DB_DIR = "chroma_db"
MODEL_NAME = "BAAI/bge-small-en-v1.5"

with open(CHUNKS_FILE, encoding="utf-8") as f:
    chunks = json.load(f)
print(f"Loaded {len(chunks)} chunks")

model = SentenceTransformer(MODEL_NAME)

client = chromadb.PersistentClient(path=DB_DIR)
try:
    client.delete_collection("mars_reports")  # fresh start on re-runs
except Exception:
    pass
collection = client.create_collection("mars_reports", metadata={"hnsw:space": "cosine"})

texts = [c["text"] for c in chunks]
embeddings = model.encode(texts, batch_size=32, normalize_embeddings=True,
                          show_progress_bar=True).tolist()

BATCH = 100
for i in range(0, len(chunks), BATCH):
    batch = chunks[i:i + BATCH]
    collection.add(
        ids=[c["chunk_id"] for c in batch],
        documents=[c["text"] for c in batch],
        embeddings=embeddings[i:i + BATCH],
        metadatas=[{
            "report_id": c["report_id"],
            "title": c["title"],
            "topic": c["topic"],
            "url": c["url"],
            "page": c["page"],
        } for c in batch],
    )
print(f"Stored {collection.count()} chunks in Chroma")

# Quick test search
query = "Why is radiation a danger for astronauts going to Mars?"
q_emb = model.encode(
    ["Represent this sentence for searching relevant passages: " + query],
    normalize_embeddings=True,
).tolist()
results = collection.query(query_embeddings=q_emb, n_results=3)

print(f"\nTest question: {query}\n")
for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print(f"[{meta['title'][:60]} | page {meta['page']}]")
    print(doc[:250], "...\n")