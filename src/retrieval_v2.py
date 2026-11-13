import os
import json

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import chromadb
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder

EMBED_MODEL = "BAAI/bge-small-en-v1.5"
RERANK_MODEL = "BAAI/bge-reranker-base"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
CANDIDATES = 20      # taken from each search
FINAL_K = 8          # chunks sent to the LLM
DECLINE_THRESHOLD = 0.0   # tuned below

embedder = SentenceTransformer(EMBED_MODEL)
reranker = CrossEncoder(RERANK_MODEL)
collection = chromadb.PersistentClient(path="chroma_db").get_collection("mars_reports")

with open("data/chunks.json", encoding="utf-8") as f:
    CHUNKS = json.load(f)
BM25 = BM25Okapi([c["text"].lower().split() for c in CHUNKS])
ID_TO_CHUNK = {c["chunk_id"]: c for c in CHUNKS}


def vector_search(question):
    emb = embedder.encode([QUERY_PREFIX + question], normalize_embeddings=True).tolist()
    res = collection.query(query_embeddings=emb, n_results=CANDIDATES)
    return res["ids"][0]


def keyword_search(question):
    scores = BM25.get_scores(question.lower().split())
    top = sorted(range(len(CHUNKS)), key=lambda i: scores[i], reverse=True)[:CANDIDATES]
    return [CHUNKS[i]["chunk_id"] for i in top]


def rrf(lists, k=60):
    """Reciprocal Rank Fusion: merge ranked lists."""
    score = {}
    for ranked in lists:
        for rank, cid in enumerate(ranked):
            score[cid] = score.get(cid, 0) + 1 / (k + rank + 1)
    return sorted(score, key=score.get, reverse=True)


def retrieve_v2(question, verbose=False):
    """Returns (hits, top_score). hits = [(text, metadata), ...]"""
    merged = rrf([vector_search(question), keyword_search(question)])[: CANDIDATES * 2]
    pairs = [(question, ID_TO_CHUNK[cid]["text"]) for cid in merged]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(merged, scores), key=lambda x: x[1], reverse=True)[:FINAL_K]

    hits = []
    for cid, s in ranked:
        c = ID_TO_CHUNK[cid]
        meta = {k: c[k] for k in ("report_id", "title", "topic", "url", "page")}
        hits.append((c["text"], meta))
        if verbose:
            print(f"  {s:6.2f}  {c['title'][:50]} | p{c['page']}")
    return hits, float(ranked[0][1])


if __name__ == "__main__":
    for q in [
        "How long does a one-way trip to Mars take in the Design Reference Architecture 5.0?",
        "What are the main health risks from space radiation?",
        "Who won the 2022 FIFA World Cup?",
        "What is the weather on Mars today?",
        "What is the recipe for chocolate cake?",
    ]:
        print(f"\n{q}")
        _, top = retrieve_v2(q, verbose=True)
        print(f"  TOP SCORE: {top:.2f}")