import os
import json
import time
import requests

API_URL = "https://ntrs.nasa.gov/api/citations/search"
PDF_DIR = os.path.join("data", "raw_pdfs")
META_FILE = os.path.join("data", "reports_metadata.json")

TOPICS = {
    "radiation": "Mars mission radiation astronauts",
    "life_support": "Mars life support system",
    "spacecraft_design": "Mars transit habitat spacecraft",
    "mission_planning": "human Mars mission architecture",
}
REPORTS_PER_TOPIC = 5

os.makedirs(PDF_DIR, exist_ok=True)
metadata = []

for topic, query in TOPICS.items():
    print(f"\n--- Topic: {topic} ---")
    params = {"q": query, "page.size": 30}
    resp = requests.get(API_URL, params=params, timeout=30)
    resp.raise_for_status()
    results = resp.json().get("results", [])

    count = 0
    for item in results:
        if count >= REPORTS_PER_TOPIC:
            break

        # find a downloadable PDF link
        pdf_link = None
        for d in item.get("downloads", []):
            link = d.get("links", {}).get("pdf")
            if link:
                pdf_link = link
                break
        if not pdf_link:
            continue

        report_id = str(item["id"])
        filename = f"{report_id}.pdf"
        path = os.path.join(PDF_DIR, filename)

        if not os.path.exists(path):
            url = "https://ntrs.nasa.gov" + pdf_link
            try:
                r = requests.get(url, timeout=60)
                r.raise_for_status()
                with open(path, "wb") as f:
                    f.write(r.content)
            except Exception as e:
                print(f"  Skipped {report_id}: {e}")
                continue
            time.sleep(1)  # be polite to NASA's server

        metadata.append({
            "id": report_id,
            "title": item.get("title", "Untitled"),
            "topic": topic,
            "file": filename,
            "url": f"https://ntrs.nasa.gov/citations/{report_id}",
        })
        print(f"  Downloaded: {item.get('title', '')[:70]}")
        count += 1

with open(META_FILE, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

print(f"\nDone. {len(metadata)} reports saved.")