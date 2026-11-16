import re
import time

import streamlit as st

st.set_page_config(page_title="Mars Mission Research Assistant", page_icon="🚀", layout="wide")


@st.cache_resource(show_spinner="Loading models (first time only)...")
def load_pipeline():
    from ask import retrieve, build_prompt, call_llm
    from retrieval_v2 import retrieve_v2
    return retrieve, retrieve_v2, build_prompt, call_llm


retrieve, retrieve_v2, build_prompt, call_llm = load_pipeline()

# ---------- sidebar ----------
with st.sidebar:
    st.title("🚀 Mars Mission Assistant")
    st.write("Ask questions about human missions to Mars. Answers come only from "
             "NASA technical reports and cite the exact report and page.")
    mode = st.radio(
        "Retrieval mode",
        ["Accurate (hybrid + reranker)", "Fast (vector search only)"],
        help="Accurate mode takes about 10-20 s. Fast mode takes about 3-5 s.",
    )
    st.markdown("**Topics covered**\n- Radiation\n- Life support\n- Spacecraft design\n- Mission planning")
    st.caption("19 NASA NTRS reports · ~870 chunks · Gemini for answers")

# ---------- main ----------
st.header("Mars Mission Research Assistant")

examples = [
    "Why is sending humans to Mars so difficult?",
    "What are the main health risks from space radiation?",
    "What is NASA's career radiation limit for astronauts?",
    "Who won the 2022 FIFA World Cup?",
]
st.caption("Try an example:")
cols = st.columns(len(examples))
for col, ex in zip(cols, examples):
    if col.button(ex, use_container_width=True):
        st.session_state["question"] = ex

question = st.text_input("Your question", key="question",
                         placeholder="e.g. How does life support work on a Mars mission?")

if st.button("Ask", type="primary") and question.strip():
    start = time.time()
    with st.spinner("Searching NASA reports and writing the answer..."):
        if mode.startswith("Accurate"):
            hits, _ = retrieve_v2(question)
        else:
            hits = retrieve(question)
        answer, model = call_llm(build_prompt(question, hits))
    elapsed = time.time() - start

    if not answer:
        st.error("The language model is busy or offline. Please try again in a minute.")
    else:
        declined = "do not contain enough information" in answer
        st.subheader("Answer")
        if declined:
            st.warning(answer)
        else:
            st.markdown(answer)
        c1, c2, c3 = st.columns(3)
        c1.metric("Response time", f"{elapsed:.1f} s")
                c2.caption(f"Model: {model}")
        c3.metric("Chunks retrieved", len(hits))

        used = set()
        for group in re.findall(r"\[([\d,\s]+)\]", answer):
            used.update(int(n) for n in re.findall(r"\d+", group))
        valid = [n for n in sorted(used) if 1 <= n <= len(hits)]

                if valid:
            st.subheader("Sources")
            groups = {}
            for n in valid:
                text, meta = hits[n - 1]
                key = (meta["report_id"], meta["page"])
                if key not in groups:
                    groups[key] = {"meta": meta, "nums": [], "texts": []}
                groups[key]["nums"].append(n)
                groups[key]["texts"].append(text)

            for g in groups.values():
                meta = g["meta"]
                label = ", ".join(f"[{n}]" for n in g["nums"])
                with st.expander(f"{label} {meta['title']} (page {meta['page']})"):
                    for t in g["texts"]:
                        st.write(t)
                        st.divider()
                    st.markdown(f"[Open report on NASA NTRS]({meta['url']})")