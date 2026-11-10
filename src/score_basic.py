import json
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "evaluation/results_baseline.json"
res = json.load(open(path, encoding="utf-8"))

answerable = [r for r in res if r["answerable"]]
off_topic = [r for r in res if not r["answerable"]]

false_declines = [r for r in answerable if r["declined"]]
correct_declines = [r for r in off_topic if r["declined"]]
with_citations = [r for r in answerable if not r["declined"] and r["cited"]]
answered = [r for r in answerable if not r["declined"]]

print(f"File: {path}")
print(f"Questions: {len(res)} ({len(answerable)} answerable, {len(off_topic)} off-topic)")
print(f"Decline accuracy: {len(correct_declines)}/{len(off_topic)}")
print(f"False declines:   {len(false_declines)}/{len(answerable)}  ids={[r['id'] for r in false_declines]}")
print(f"Answers with citations: {len(with_citations)}/{len(answered)}")
print(f"Average latency: {sum(r['latency_seconds'] for r in res)/len(res):.2f}s")