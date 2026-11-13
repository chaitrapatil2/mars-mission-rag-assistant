import json
import random
import re
import time

from ask import call_llm

chunks = json.load(open("data/chunks.json", encoding="utf-8"))
test_set = json.load(open("evaluation/test_set.json", encoding="utf-8"))
json.dump(test_set, open("evaluation/test_set_12_backup.json", "w", encoding="utf-8"), indent=2)

random.seed(7)
by_topic = {}
for c in chunks:
    if len(c["text"].split()) >= 120 and c["page"] > 1:
        by_topic.setdefault(c["topic"], []).append(c)

next_id = max(t["id"] for t in test_set) + 1
PER_TOPIC = 4

for topic, items in by_topic.items():
    random.shuffle(items)
    made = 0
    for c in items:
        if made >= PER_TOPIC:
            break
        prompt = f"""Read this passage from a NASA report and write ONE factual question that this passage answers,
plus a short answer (1-2 sentences) using ONLY the passage.
The question must make sense on its own: never say "the passage" or "the text".
Reply with only JSON: {{"question": "...", "answer": "..."}}

PASSAGE:
{c['text']}"""
        out, _ = call_llm(prompt)
        if not out:
            continue
        m = re.search(r"\{.*\}", out, re.S)
        try:
            qa = json.loads(m.group(0))
        except Exception:
            continue
        test_set.append({
            "id": next_id, "question": qa["question"], "ground_truth": qa["answer"],
            "topic": topic, "answerable": True,
            "source_report_id": c["report_id"], "source_page": c["page"],
        })
        print(f"[{next_id}] {topic}: {qa['question'][:80]}")
        next_id += 1
        made += 1
        time.sleep(2)

for q in [
    "Who was the first person to walk on Mars?",
    "How much does a SpaceX Starship launch cost?",
    "What is the capital of France?",
    "How do I treat a common cold at home?",
]:
    test_set.append({"id": next_id, "question": q, "ground_truth": "", "topic": "none", "answerable": False})
    next_id += 1

json.dump(test_set, open("evaluation/test_set.json", "w", encoding="utf-8"), indent=2)
print(f"\nTest set now has {len(test_set)} questions")