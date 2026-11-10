import re
import time
from flask import Flask, request, jsonify
from ask import retrieve, build_prompt, call_llm

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/ask", methods=["POST"])
def ask_endpoint():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": 'Send JSON like {"question": "..."}'}), 400

    start = time.time()
    hits = retrieve(question)
    answer, model_used = call_llm(build_prompt(question, hits))
    if not answer:
        return jsonify({"error": "The language model is busy. Try again shortly."}), 503

    # keep only citation numbers that really exist
    used = set()
    for group in re.findall(r"\[([\d,\s]+)\]", answer):
        used.update(int(n) for n in re.findall(r"\d+", group))

    sources, seen = [], set()
    for n in sorted(used):
        if 1 <= n <= len(hits):
            m = hits[n - 1][1]
            key = (m["report_id"], m["page"])
            if key in seen:
                continue
            seen.add(key)
            sources.append({"title": m["title"], "page": m["page"], "url": m["url"]})

    return jsonify({
        "question": question,
        "answer": answer,
        "sources": sources,
        "model": model_used,
        "latency_seconds": round(time.time() - start, 2),
    })


if __name__ == "__main__":
    app.run(port=5000, debug=False)