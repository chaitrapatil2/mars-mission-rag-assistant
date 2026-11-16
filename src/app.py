import re
import time

import streamlit as st

st.set_page_config(page_title="Mars Mission Research Assistant", page_icon="🚀", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Inter:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
    background:
        radial-gradient(circle at 15% 0%, rgba(255,107,61,0.14), transparent 40%),
        radial-gradient(circle at 90% 10%, rgba(80,110,255,0.14), transparent 40%),
        #0B0F1E;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; max-width: 1150px; }

/* hero */
.hero {
    padding: 38px 40px;
    border-radius: 22px;
    background: linear-gradient(135deg, rgba(255,107,61,0.20), rgba(20,26,51,0.9) 55%, rgba(80,110,255,0.18));
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0 10px 40px rgba(0,0,0,0.35);
    margin-bottom: 22px;
}
.hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.8rem; font-weight: 700; margin: 0 0 8px 0;
    background: linear-gradient(90deg, #FFB48F, #FF6B3D 60%, #FF3D6E);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero p { color: #B9B4C9; font-size: 1.05rem; margin: 0 0 18px 0; max-width: 720px; }
.pill {
    display: inline-block; padding: 6px 14px; margin: 0 8px 8px 0;
    border-radius: 999px; font-size: 0.82rem; color: #EDE8E0;
    background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.12);
}

/* section labels */
.label {
    font-family: 'Space Grotesk', sans-serif; letter-spacing: 0.12em;
    text-transform: uppercase; font-size: 0.78rem; color: #FF9A73; margin: 18px 0 8px 0;
}

/* buttons */
.stButton > button {
    border-radius: 12px; border: 1px solid rgba(255,255,255,0.14);
    background: rgba(255,255,255,0.05); color: #EDE8E0; transition: all .2s;
}
.stButton > button:hover {
    border-color: #FF6B3D; background: rgba(255,107,61,0.14); transform: translateY(-2px);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #FF6B3D, #FF3D6E); border: none; color: white;
    font-weight: 600; padding: 0.55rem 2rem;
}
.stButton > button[kind="primary"]:hover { box-shadow: 0 6px 22px rgba(255,80,80,0.45); }

/* input */
.stTextInput input {
    background: #141A33; border: 1px solid rgba(255,255,255,0.16);
    border-radius: 12px; color: #EDE8E0; padding: 14px;
}
.stTextInput input:focus { border-color: #FF6B3D; box-shadow: 0 0 0 1px #FF6B3D; }

/* answer card */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(20,26,51,0.75); border: 1px solid rgba(255,255,255,0.10);
    border-radius: 18px; box-shadow: 0 8px 30px rgba(0,0,0,0.3);
}
.cite {
    display: inline-block; padding: 0 7px; border-radius: 6px; font-size: 0.8em;
    font-weight: 600; color: #FFB48F; background: rgba(255,107,61,0.16);
    border: 1px solid rgba(255,107,61,0.35);
}

/* stat cards */
.stat {
    padding: 16px 20px; border-radius: 14px; background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.10);
}
.stat .v { font-family: 'Space Grotesk', sans-serif; font-size: 1.7rem; font-weight: 700; color: #FFB48F; }
.stat .k { font-size: 0.8rem; color: #9C98AE; text-transform: uppercase; letter-spacing: 0.08em; }

/* decline box */
.decline {
    padding: 18px 22px; border-radius: 14px; background: rgba(255,190,60,0.10);
    border: 1px solid rgba(255,190,60,0.45); color: #FFD98A; font-size: 1.02rem;
}

/* sources */
div[data-testid="stExpander"] {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.10);
    border-radius: 12px;
}

/* sidebar */
section[data-testid="stSidebar"] {
    background: #0E1328; border-right: 1px solid rgba(255,255,255,0.08);
}
.footer { text-align:center; color:#7C7890; font-size:0.82rem; margin-top:40px; padding-bottom:20px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading models (first time only)...")
def load_pipeline():
    from ask import retrieve, build_prompt, call_llm
    from retrieval_v2 import retrieve_v2
    return retrieve, retrieve_v2, build_prompt, call_llm


retrieve, retrieve_v2, build_prompt, call_llm = load_pipeline()

# ---------- sidebar ----------
with st.sidebar:
    st.markdown("## 🚀 Mission Control")
    mode = st.radio(
        "Retrieval mode",
        ["Accurate (hybrid + reranker)", "Fast (vector search only)"],
        help="Accurate takes about 10-20 s. Fast takes about 3-5 s.",
    )
    st.markdown("---")
    st.markdown("**Knowledge base**")
    st.markdown("- ☢️ Radiation\n- 🫁 Life support\n- 🛰️ Spacecraft design\n- 🗺️ Mission planning")
    st.markdown("---")
    st.markdown("**How it works**")
    st.caption("1. Your question is embedded\n\n2. Vector + keyword search find passages\n\n"
               "3. A reranker picks the best 8\n\n4. Gemini answers using only those passages and cites them")

# ---------- hero ----------
st.markdown(
    """
<div class="hero">
  <h1>Mars Mission Research Assistant</h1>
  <p>Ask anything about sending humans to Mars. Every answer is grounded in NASA technical
  reports and cites the exact report and page, or says so when the reports don't know.</p>
  <span class="pill">📄 19 NASA reports</span>
  <span class="pill">🧩 ~870 searchable chunks</span>
  <span class="pill">🔎 Hybrid retrieval + reranker</span>
  <span class="pill">📌 Cited answers</span>
  <span class="pill">🚫 Declines off-topic questions</span>
</div>
""",
    unsafe_allow_html=True,
)

# ---------- examples ----------
examples = [
    ("🚀 Why is Mars hard?", "Why is sending humans to Mars so difficult?"),
    ("☢️ Radiation risks", "What are the main health risks from space radiation?"),
    ("📏 Radiation limit", "What is NASA's career radiation limit for astronauts?"),
    ("⚽ Off-topic test", "Who won the 2022 FIFA World Cup?"),
]
st.markdown('<div class="label">Try an example</div>', unsafe_allow_html=True)
cols = st.columns(len(examples))
for col, (label, full_question) in zip(cols, examples):
    if col.button(label, use_container_width=True):
        st.session_state["question"] = full_question

st.markdown('<div class="label">Your question</div>', unsafe_allow_html=True)
question = st.text_input("question", key="question", label_visibility="collapsed",
                         placeholder="e.g. How does life support work on a Mars mission?")

ask_clicked = st.button("Ask the reports  🚀", type="primary")

if ask_clicked and question.strip():
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

        st.markdown('<div class="label">Answer</div>', unsafe_allow_html=True)
        if declined:
            st.markdown(f'<div class="decline">🛑 {answer}</div>', unsafe_allow_html=True)
        else:
            pretty = re.sub(r"\[(\d+(?:\s*,\s*\d+)*)\]",
                            lambda m: f'<span class="cite">[{m.group(1)}]</span>', answer)
            with st.container(border=True):
                st.markdown(pretty, unsafe_allow_html=True)

        short_mode = "Accurate" if mode.startswith("Accurate") else "Fast"
        s1, s2, s3 = st.columns(3)
        s1.markdown(f'<div class="stat"><div class="v">{elapsed:.1f} s</div>'
                    f'<div class="k">Response time</div></div>', unsafe_allow_html=True)
        s2.markdown(f'<div class="stat"><div class="v">{short_mode}</div>'
                    f'<div class="k">Retrieval mode</div></div>', unsafe_allow_html=True)
        s3.markdown(f'<div class="stat"><div class="v">{len(hits)}</div>'
                    f'<div class="k">Passages retrieved</div></div>', unsafe_allow_html=True)
        st.caption(f"Model: {model}")

        used = set()
        for group in re.findall(r"\[([\d,\s]+)\]", answer):
            used.update(int(n) for n in re.findall(r"\d+", group))
        valid = [n for n in sorted(used) if 1 <= n <= len(hits)]

        if valid:
            st.markdown('<div class="label">Sources</div>', unsafe_allow_html=True)
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
                with st.expander(f"{label}  {meta['title']} (page {meta['page']})"):
                    for t in g["texts"]:
                        st.write(t)
                        st.divider()
                    st.markdown(f"[Open report on NASA NTRS ↗]({meta['url']})")

st.markdown(
    '<div class="footer">Built with Python · ChromaDB · BM25 · BGE reranker · Gemini · Streamlit<br>'
    'Data: NASA Technical Reports Server (NTRS)</div>',
    unsafe_allow_html=True,
)