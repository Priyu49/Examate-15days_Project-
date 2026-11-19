import csv
import html
import io
import os

import requests
import streamlit as st

API_URL = os.getenv("MITRAMAATI_API", "http://127.0.0.1:8000")

# (name, unit, default, step, display format)
SOIL_PARAMETERS = [
    ("Nitrogen (N)", "kg/ha", 200.0, 10.0, "%.1f"),
    ("Phosphorus (P)", "kg/ha", 8.0, 1.0, "%.1f"),
    ("Potassium (K)", "kg/ha", 150.0, 10.0, "%.1f"),
    ("Organic Carbon (OC)", "%", 0.6, 0.05, "%.2f"),
    ("Soil pH", "pH", 6.5, 0.1, "%.1f"),
    ("Sulphur (S)", "ppm", 15.0, 1.0, "%.1f"),
    ("Zinc (Zn)", "ppm", 0.8, 0.1, "%.2f"),
    ("Boron (B)", "ppm", 0.4, 0.1, "%.2f"),
    ("Iron (Fe)", "ppm", 6.0, 0.5, "%.1f"),
    ("Manganese (Mn)", "ppm", 3.0, 0.5, "%.1f"),
    ("Copper (Cu)", "ppm", 0.3, 0.1, "%.2f"),
    ("Electrical Conductivity (EC)", "dS/m", 0.5, 0.1, "%.2f"),
]
DEFAULTS = {name: default for name, _, default, _, _ in SOIL_PARAMETERS}

SAMPLES = {
    "Default values": DEFAULTS,
    "Mixed field (red + yellow + green)": {
        "Nitrogen (N)": 600.0, "Phosphorus (P)": 5.0, "Potassium (K)": 200.0,
        "Organic Carbon (OC)": 1.2, "Soil pH": 6.5, "Sulphur (S)": 15.0,
        "Zinc (Zn)": 1.5, "Boron (B)": 0.4, "Iron (Fe)": 6.0,
        "Manganese (Mn)": 3.0, "Copper (Cu)": 0.6, "Electrical Conductivity (EC)": 0.5,
    },
    "Nutrient-poor field": {
        "Nitrogen (N)": 150.0, "Phosphorus (P)": 4.0, "Potassium (K)": 80.0,
        "Organic Carbon (OC)": 0.3, "Soil pH": 5.5, "Sulphur (S)": 5.0,
        "Zinc (Zn)": 0.3, "Boron (B)": 0.2, "Iron (Fe)": 3.0,
        "Manganese (Mn)": 1.0, "Copper (Cu)": 0.1, "Electrical Conductivity (EC)": 0.2,
    },
}

TILE_STYLES = {  # traffic-light colours: background, border, text
    "red": ("#fdecea", "#d93025", "#8a1c14"),
    "yellow": ("#fff8e1", "#f9ab00", "#7a5200"),
    "green": ("#e6f4ea", "#1e8e3e", "#0d5224"),
}
STATUS_TO_COLOR = {"Low": "red", "Medium": "yellow", "High": "green"}
EXAMPLES = [
    "classify nitrogen 200",
    "classify phosphorus 5",
    "What does low phosphorus mean?",
    "Why is organic carbon important?",
]

st.set_page_config(page_title="MitraMaati", page_icon="🌱", layout="wide")


# ---------------------------------------------------------------- API helpers
def api_post(path, payload):
    """POST to the FastAPI backend; returns (json, error_message)."""
    try:
        r = requests.post(f"{API_URL}{path}", json=payload, timeout=60)
        if r.status_code >= 400:
            if r.headers.get("content-type", "").startswith("application/json"):
                detail = r.json().get("detail", r.text)
            else:
                detail = r.text
            return None, f"API error {r.status_code}: {detail}"
        return r.json(), None
    except requests.exceptions.RequestException:
        return None, (f"Cannot reach the API at {API_URL}. "
                      "Start it with: uvicorn main:app --reload --reload-exclude ui")


def api_online():
    try:
        return requests.get(f"{API_URL}/health", timeout=1.5).status_code == 200
    except requests.exceptions.RequestException:
        return False


def ask_backend(question, mode):
    if mode == "/agent":
        return api_post("/agent", {"query": question, "thread_id": st.session_state.thread_id})
    return api_post("/ask", {"question": question, "top_k": 3})


def send_feedback(index, rating):
    msg = st.session_state.messages[index]
    _, err = api_post("/feedback", {
        "question": msg.get("question", ""), "answer": msg["content"],
        "rating": rating, "thread_id": st.session_state.thread_id,
    })
    if err:
        st.session_state.flash = err
    else:
        msg["feedback"] = rating


def resume_agent(index, approve):
    data, err = api_post("/agent", {"thread_id": st.session_state.thread_id, "approve": approve})
    if err:
        st.session_state.flash = err
        return
    msg = st.session_state.messages[index]
    msg["content"] = data["response"]
    msg["citations"] = data.get("citations", msg.get("citations", []))
    msg["pending"] = False
    msg["note"] = "✅ Approved by farmer" if approve else "⛔ Rejected by farmer"


def queue_question(text):
    st.session_state.queued = text


def apply_sample():
    values = SAMPLES[st.session_state.sample_choice]
    for idx, (name, *_rest) in enumerate(SOIL_PARAMETERS):
        st.session_state[f"soil_{idx}"] = float(values[name])
    st.session_state.tiles = None


def reset_soil():
    st.session_state.sample_choice = "Default values"
    apply_sample()


# ---------------------------------------------------------------- state
st.session_state.setdefault("messages", [])
st.session_state.setdefault("thread_id", None)
st.session_state.setdefault("tiles", None)
st.session_state.setdefault("flash", None)
st.session_state.setdefault("queued", None)
st.session_state.setdefault("sample_choice", "Default values")
for _i, (_n, _u, _d, _s, _f) in enumerate(SOIL_PARAMETERS):
    st.session_state.setdefault(f"soil_{_i}", float(_d))

online = api_online()

with st.sidebar:
    st.title("🌱 MitraMaati")
    st.caption("Soil Health Card assistant")
    if online:
        st.success("API online")
    else:
        st.error("API offline")
        st.caption("Start it: `uvicorn main:app --reload --reload-exclude ui`")
        st.button("↻ Check again")

    mode = st.radio("Backend endpoint", ["/ask", "/agent"],
                    help="/ask = grounded RAG answer. /agent = LangGraph agent with memory and approval.")
    if mode == "/agent" and st.session_state.thread_id:
        st.caption(f"Conversation id: `{st.session_state.thread_id[:8]}`")

    st.markdown("**Try asking**")
    for n, example in enumerate(EXAMPLES):
        st.button(example, key=f"ex_{n}", on_click=queue_question, args=(example,),
                  use_container_width=True)

    if st.session_state.messages:
        lines = []
        for m in st.session_state.messages:
            who = "Farmer" if m["role"] == "user" else "MitraMaati"
            lines.append(f"{who}: {m['content']}")
        st.download_button("⬇️ Download conversation", "\n\n".join(lines),
                           file_name="mitramaati_chat.txt", mime="text/plain",
                           use_container_width=True)

    if st.button("🗑️ New conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = None
        st.rerun()

if st.session_state.flash:
    st.error(st.session_state.flash)
    st.session_state.flash = None

tab_chat, tab_card = st.tabs(["💬 Chat", "🚦 Soil card"])

# ---------------------------------------------------------------- chat tab
with tab_chat:
    if not st.session_state.messages:
        st.info("Ask a question below, or pick one from **Try asking** in the sidebar. "
                "Use **/agent** for questions like 'classify nitrogen 200'.")

    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] != "assistant":
                continue

            status = msg.get("status")
            if status in STATUS_TO_COLOR:
                bg, border, text = TILE_STYLES[STATUS_TO_COLOR[status]]
                st.markdown(
                    f"<span style='background:{bg};color:{text};border:1px solid {border};"
                    f"padding:2px 10px;border-radius:12px;font-weight:700;font-size:0.8rem'>"
                    f"{html.escape(status.upper())}</span>",
                    unsafe_allow_html=True,
                )
            if msg.get("note"):
                st.caption(msg["note"])

            citations = msg.get("citations") or []
            if citations:
                with st.expander(f"📚 Citations ({len(citations)})"):
                    for c in citations:
                        src = c.get("source", "")
                        link = f"[source]({src})" if str(src).startswith("http") else src
                        page = c.get("page")
                        page_txt = f", page {page}" if page else ""
                        st.markdown(f"- **{c.get('title', 'Soil parameter')}**{page_txt} — {link}")

            if msg.get("pending"):
                st.warning("Farmer approval needed before this recommendation is released.")
                a, b, _ = st.columns([1, 1, 6])
                a.button("✅ Approve", key=f"ok_{i}", on_click=resume_agent, args=(i, True))
                b.button("⛔ Reject", key=f"no_{i}", on_click=resume_agent, args=(i, False))
            elif msg.get("feedback"):
                st.caption("Thanks, your " + ("👍" if msg["feedback"] == "up" else "👎") + " was saved.")
            else:
                a, b, _ = st.columns([1, 1, 8])
                a.button("👍", key=f"up_{i}", on_click=send_feedback, args=(i, "up"))
                b.button("👎", key=f"down_{i}", on_click=send_feedback, args=(i, "down"))

    typed = st.chat_input("Ask about your soil, e.g. 'What does low phosphorus mean?'")
    queued = st.session_state.queued
    st.session_state.queued = None
    question = typed or queued

    if question:
        if any(m.get("pending") for m in st.session_state.messages):
            st.session_state.flash = "Approve or reject the pending recommendation first."
            st.rerun()
        st.session_state.messages.append({"role": "user", "content": question})
        with st.spinner("Thinking..."):
            data, err = ask_backend(question, mode)
        if err:
            st.session_state.flash = err
        else:
            tool_out = data.get("tool_output") or {}
            msg = {
                "role": "assistant",
                "question": question,
                "content": data.get("response") or data.get("answer", ""),
                "citations": data.get("citations", []),
                "status": tool_out.get("status"),
            }
            if mode == "/agent":
                st.session_state.thread_id = data["thread_id"]
                msg["pending"] = data["status"] == "pending_approval"
            st.session_state.messages.append(msg)
        st.rerun()

# ---------------------------------------------------------------- soil card tab
with tab_card:
    st.subheader("Traffic-light soil card")
    st.caption("Enter the 12 values from your Soil Health Card. 🔴 Low · 🟡 Medium · 🟢 High")

    top_a, top_b = st.columns([3, 1])
    top_a.selectbox("Load sample values", list(SAMPLES), key="sample_choice", on_change=apply_sample)
    top_b.write("")
    top_b.button("↺ Reset", on_click=reset_soil, use_container_width=True)

    with st.form("soil_form"):
        cols = st.columns(3)
        values = {}
        for idx, (name, unit, _default, step, fmt) in enumerate(SOIL_PARAMETERS):
            values[name] = cols[idx % 3].number_input(
                f"{name} ({unit})", min_value=0.0, step=step, format=fmt, key=f"soil_{idx}")
        submitted = st.form_submit_button("Classify my soil", type="primary")

    if submitted:
        data, err = api_post("/soil-card", {"values": values})
        if err:
            st.error(err)
        else:
            st.session_state.tiles = data["tiles"]

    tiles = st.session_state.tiles
    if tiles:
        counts = {c: sum(t.get("color_code") == c for t in tiles) for c in TILE_STYLES}
        m1, m2, m3 = st.columns(3)
        m1.metric("🔴 Low", counts["red"])
        m2.metric("🟡 Medium", counts["yellow"])
        m3.metric("🟢 High", counts["green"])

        chosen = st.multiselect("Show", ["Low", "Medium", "High"], default=["Low", "Medium", "High"])
        shown = [t for t in tiles if t.get("status") in chosen]

        cards = []
        for t in shown:
            bg, border, text = TILE_STYLES.get(t.get("color_code"), TILE_STYLES["yellow"])
            src = html.escape(str(t.get("source_url", "")))
            page = t.get("page")
            cite = f"Cited from page {page}" if page else "Source: Soil Health Card ratings"
            cards.append(
                f"<div style='background:{bg};border-left:8px solid {border};border-radius:10px;"
                f"padding:12px 14px;color:{text}'>"
                f"<div style='font-weight:700'>{html.escape(t['parameter'])}</div>"
                f"<div style='font-size:1.5rem;font-weight:800'>{t['measured_value']} "
                f"<small>{html.escape(t.get('unit', ''))}</small></div>"
                f"<div style='font-weight:700'>{html.escape(t['status'].upper())}</div>"
                f"<div style='font-size:0.85rem;margin:4px 0'>{html.escape(t.get('meaning', ''))}</div>"
                f"<div style='font-size:0.85rem;margin:4px 0'><b>Advice:</b> "
                f"{html.escape(t.get('recommendation', ''))}</div>"
                f"<div style='font-size:0.75rem'>📄 {html.escape(cite)} · "
                f"<a href='{src}' target='_blank' style='color:{text}'>source</a></div></div>"
            )
        st.markdown(
            "<div style='display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));"
            "gap:14px;align-items:stretch'>" + "".join(cards) + "</div>",
            unsafe_allow_html=True,
        )

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["parameter", "value", "unit", "status", "recommendation"])
        for t in tiles:
            writer.writerow([t["parameter"], t["measured_value"], t.get("unit", ""),
                             t["status"], t.get("recommendation", "")])
        st.download_button("⬇️ Download results (CSV)", buf.getvalue(),
                           file_name="soil_card.csv", mime="text/csv")
