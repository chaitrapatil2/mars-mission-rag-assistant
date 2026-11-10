import os
import json
import pymupdf

PDF_DIR = os.path.join("data", "raw_pdfs")
OUT_DIR = os.path.join("data", "extracted")
META_FILE = os.path.join("data", "reports_metadata.json")

os.makedirs(OUT_DIR, exist_ok=True)

with open(META_FILE, encoding="utf-8") as f:
    reports = json.load(f)

for rep in reports:
    pdf_path = os.path.join(PDF_DIR, rep["file"])
    doc = pymupdf.open(pdf_path)

    pages = []
    for page_num, page in enumerate(doc, start=1):
        text = " ".join(page.get_text().split())  # clean extra spaces/newlines
        if text:
            pages.append({"page": page_num, "text": text})

    total_chars = sum(len(p["text"]) for p in pages)

    out = {
        "id": rep["id"],
        "title": rep["title"],
        "topic": rep["topic"],
        "url": rep["url"],
        "pages": pages,
    }
    with open(os.path.join(OUT_DIR, rep["id"] + ".json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    warning = "  <-- very little text, maybe scanned" if total_chars < 2000 else ""
    print(f"{rep['id']}: {len(pages)} pages, {total_chars} chars  {rep['title'][:40]}{warning}")

print("\nDone.")