import os
import re
import time

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from google import genai

load_dotenv()

DB_DIR = "chroma_db"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
# tried in order; if one is busy or missing, the next is used
MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.8-flash",
]
TOP_K = 5
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

embedder = SentenceTransformer(EMBED_MODEL)
collection = chromadb.PersistentClient(path=DB_DIR).get_collection("mars_reports")
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def retrieve(question):
    """Find the TOP_K most relevant chunks for the question."""
    emb = embedder.encode([QUERY_PREFIX + question], normalize_embeddings=True).tolist()
    res = collection.query(query_embeddings=emb, n_results=TOP_K)
    return list(zip(res["documents"][0], res["metadatas"][0]))


def build_prompt(question, hits):
    """Label the chunks [1]..[5] and give the LLM strict rules."""
    sources = "\n\n".join(
        f"[{i}] ({m['title']}, page {m['page']})\n{doc}"
        for i, (doc, m) in enumerate(hits, start=1)
    )
    return f"""You are a research assistant for human missions to Mars.
Answer the question using ONLY the numbered sources below.

Rules:
- After every claim, cite the source number like [1] or [2].
- If the sources do not contain the answer, reply exactly: "The reports do not contain enough information to answer this."
- Do not use outside knowledge. Keep the answer clear and under 200 words.

SOURCES:
{sources}

QUESTION: {question}

ANSWER:"""


def call_llm(prompt):
    """Try each model up to 2 times, waiting longer between attempts."""
    for model in MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(model=model, contents=prompt)
                return response.text, model
            except Exception as e:
                print(f"  ({model}, attempt {attempt + 1} failed: {str(e)[:70]})")
                time.sleep(3 * (attempt + 1))
    return None, None


def ask(question):
    hits = retrieve(question)
    answer, model_used = call_llm(build_prompt(question, hits))
    if not answer:
        print("\nAll models are busy right now. Please try again in a minute.")
        return

    # Citation check: which source numbers did the LLM use, and are they real?
    used = set()
    for group in re.findall(r"\[([\d,\s]+)\]", answer):
        used.update(int(n) for n in re.findall(r"\d+", group))
    valid = sorted(n for n in used if 1 <= n <= len(hits))
    invalid = sorted(n for n in used if n not in valid)

    print(f"\nANSWER (model: {model_used}):\n" + answer)
    print("\nSOURCES USED:")
    for n in valid:
        m = hits[n - 1][1]
        print(f"  [{n}] {m['title']} | page {m['page']} | {m['url']}")
    if invalid:
        print(f"\n  WARNING: the model cited non-existent sources: {invalid}")


if __name__ == "__main__":
    print("Mars Mission Research Assistant (type 'quit' to exit)")
    while True:
        q = input("\nYour question: ").strip()
        if q.lower() in ("quit", "exit", ""):
            break
        ask(q)