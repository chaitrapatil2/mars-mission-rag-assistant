import json
import re
import time

from ask import build_prompt, call_llm
from retrieval_v2 import retrieve_v2

with open("evaluation/test_set.json", encoding="utf-8") as f:
    test_set = json.load(f)

DECLINE = "The reports do not contain enough information"
results = []

for item in test_set:
    q = item["question"]
    start = time.time()
    hits, top = retrieve_v2(q)
    answer, model = call_llm(build_prompt(q, hits))
    latency = round(time.time() - start, 2)

    if not answer:
        print(f"[{item['id']}] LLM failed, skipping")
        continue

    used = set()
    for group in re.findall(r"\[([\d,\s]+)\]", answer):
        used.update(int(n) for n in re.findall(r"\d+", group))
    cited = [{"title": hits[n-1][1]["title"], "page": hits[n-1][1]["page"],
              "report_id": hits[n-1][1]["report_id"]}
             for n in sorted(used) if 1 <= n <= len(hits)]

    results.append({
        "id": item["id"], "question": q,
        "ground_truth": item["ground_truth"], "answerable": item["answerable"],
        "answer": answer, "declined": DECLINE in answer,
        "contexts": [doc for doc, _ in hits],
        "retrieved": [{"title": m["title"], "page": m["page"], "report_id": m["report_id"]}
                      for _, m in hits],
        "cited": cited, "latency_seconds": latency, "model": model,
    })
    print(f"[{item['id']}] done in {latency}s | declined={DECLINE in answer}")
    time.sleep(2)

with open("evaluation/results_v2.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved {len(results)} results to evaluation/results_v2.json")