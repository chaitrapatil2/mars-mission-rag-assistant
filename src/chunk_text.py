import os
import json

EXTRACTED_DIR = os.path.join("data", "extracted")
OUT_FILE = os.path.join("data", "chunks.json")

CHUNK_WORDS = 200    # size of each chunk
OVERLAP_WORDS = 40   # words shared with the next chunk
MIN_WORDS = 30       # drop tiny chunks (page numbers, headers)

chunks = []

for filename in sorted(os.listdir(EXTRACTED_DIR)):
    with open(os.path.join(EXTRACTED_DIR, filename), encoding="utf-8") as f:
        report = json.load(f)

    report_chunks = 0
    for page in report["pages"]:
        words = page["text"].split()
        step = CHUNK_WORDS - OVERLAP_WORDS

        for start in range(0, len(words), step):
            piece = words[start:start + CHUNK_WORDS]
            if len(piece) < MIN_WORDS:
                continue

            chunks.append({
                "chunk_id": f"{report['id']}_p{page['page']}_{start}",
                "report_id": report["id"],
                "title": report["title"],
                "topic": report["topic"],
                "url": report["url"],
                "page": page["page"],
                "text": " ".join(piece),
            })
            report_chunks += 1

    print(f"{report['id']}: {report_chunks} chunks  {report['title'][:45]}")

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2)

print(f"\nTotal chunks: {len(chunks)}")