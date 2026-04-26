import streamlit as st
import pandas as pd
from processor import build_dfa, scan_paragraph

# --------------- Page Configuration ---------------
st.set_page_config(
    page_title="DFA Word/Phrase Highlighter",
    page_icon="dfa",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------- Custom CSS ---------------
st.markdown("""
<style>
    /* ---- Import Google Font ---- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ---- Global Reset ---- */
    *, *::before, *::after { box-sizing: border-box; }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ---- Remove default Streamlit header / footer / spacing ---- */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding: 2rem 3rem 3rem 3rem !important;
        max-width: 1100px;
    }

    /* ---- Hero Header ---- */
    .hero {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 100%);
        border-radius: 14px;
        padding: 2.2rem 2.4rem;
        margin-bottom: 1.8rem;
    }
    .hero h1 {
        margin: 0 0 .35rem 0;
        font-size: 1.65rem;
        font-weight: 700;
        color: #e0e7ff;
        letter-spacing: -0.02em;
    }
    .hero p {
        margin: 0;
        font-size: 0.92rem;
        color: #a5b4fc;
        line-height: 1.55;
    }

    /* ---- Status Pill ---- */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(34,197,94,0.12);
        color: #4ade80;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 999px;
        margin-bottom: 0.7rem;
        border: 1px solid rgba(34,197,94,0.18);
        letter-spacing: 0.02em;
    }
    .status-dot {
        width: 7px; height: 7px;
        background: #4ade80;
        border-radius: 50%;
        display: inline-block;
    }

    /* ---- Cards ---- */
    .card {
        background: #1A1D26;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 1.6rem 1.8rem;
        margin-bottom: 1.4rem;
    }
    .card-title {
        font-size: 0.82rem;
        font-weight: 600;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 1rem;
    }

    /* ---- Metric Cards ---- */
    .metric-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.4rem;
    }
    .metric-card {
        flex: 1;
        background: #1A1D26;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 1.3rem 1.5rem;
        text-align: center;
    }
    .metric-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.35rem;
    }
    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #e0e7ff;
        line-height: 1.15;
    }
    .metric-value.accent { color: #818cf8; }
    .metric-value.green  { color: #4ade80; }

    /* ---- Highlighted text container ---- */
    .highlight-box {
        background: #13151c;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px;
        padding: 1.4rem 1.6rem;
        font-size: 0.95rem;
        line-height: 1.75;
        color: #d1d5db;
    }

    /* ---- Streamlit widget overrides ---- */
    .stTextArea textarea {
        background: #13151c !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 10px !important;
        color: #e5e7eb !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.92rem !important;
        padding: 1rem !important;
        transition: border-color 0.2s ease;
    }
    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99,102,241,0.15) !important;
    }

    /* Primary button */
    .stButton > button[kind="primary"],
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #818cf8) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.65rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.01em;
        transition: transform 0.15s ease, box-shadow 0.2s ease !important;
        box-shadow: 0 4px 16px rgba(99,102,241,0.25) !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 24px rgba(99,102,241,0.35) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: #1A1D26;
        border-radius: 10px;
        padding: 4px;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.55rem 1.3rem;
        font-weight: 500;
        font-size: 0.85rem;
        color: #9ca3af;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(99,102,241,0.15) !important;
        color: #a5b4fc !important;
    }
    .stTabs [data-baseweb="tab-border"] { display: none; }
    .stTabs [data-baseweb="tab-highlight"] { display: none; }

    /* DataFrame (table) overrides */
    .stDataFrame { border-radius: 10px; overflow: hidden; }

    /* Info / warning / success boxes — restyle */
    .stAlert {
        border-radius: 10px !important;
        font-size: 0.88rem !important;
    }

    /* Hide Streamlit's default label for text_area */
    .stTextArea label { display: none !important; }

    /* Footer */
    .app-footer {
        text-align: center;
        margin-top: 2.5rem;
        padding-top: 1.2rem;
        border-top: 1px solid rgba(255,255,255,0.06);
        font-size: 0.78rem;
        color: #6b7280;
    }
</style>
""", unsafe_allow_html=True)


# --------------- Build DFA Engine ---------------
if 'dfa_engine' not in st.session_state:
    st.session_state['dfa_engine'] = build_dfa()


# --------------- Hero Header ---------------
st.markdown("""
<div class="hero">
    <div class="status-pill"><span class="status-dot"></span> DFA Engine Active</div>
    <h1>Number-Quantity Recognizer</h1>
    <p>
        A DFA-powered scanner that detects <strong>[Number] [Unit]</strong> patterns in free text.
    </p>
</div>
""", unsafe_allow_html=True)


# --------------- Input Section ---------------
st.markdown('<div class="card-title">Input</div>', unsafe_allow_html=True)
user_input = st.text_area(
    "paragraph_input",
    height=180,
    placeholder="For example: 'I bought 2 kg of rice and 500 ml of milk.'"
)

recognize_clicked = st.button("Recognize Tokens", type="primary")


# --------------- Results ---------------
if recognize_clicked and user_input:
    dfa = st.session_state['dfa_engine']
    verdicts, highlighted_text = scan_paragraph(user_input, dfa)

    total_tokens = len(verdicts)
    accepted_tokens = sum(1 for v in verdicts if v[1])
    rejected_tokens = total_tokens - accepted_tokens
    acceptance_rate = (accepted_tokens / total_tokens * 100) if total_tokens > 0 else 0

    # Metrics
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-label">Total Tokens</div>
            <div class="metric-value">{total_tokens}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Accepted</div>
            <div class="metric-value green">{accepted_tokens}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Rejected</div>
            <div class="metric-value" style="color:#f87171;">{rejected_tokens}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Acceptance Rate</div>
            <div class="metric-value accent">{acceptance_rate:.1f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    tab_highlight, tab_details = st.tabs(["Highlighted Text", "Detailed Results"])

    with tab_highlight:
        st.markdown(
            f'<div class="highlight-box">{highlighted_text}</div>',
            unsafe_allow_html=True
        )

    with tab_details:
        df = pd.DataFrame(verdicts, columns=["Token / Phrase", "Accepted"])
        df["Accepted"] = df["Accepted"].apply(lambda x: "Yes" if x else "No")

        def color_accepted(val):
            if val == "Yes":
                return "color: #4ade80; font-weight: 600;"
            elif val == "No":
                return "color: #f87171; font-weight: 600;"
            return ""

        styled_df = df.style.map(color_accepted, subset=["Accepted"])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

elif recognize_clicked and not user_input:
    st.warning("Please enter a paragraph before running recognition.")

else:
    st.markdown("""
    <div class="card" style="text-align:center; color:#6b7280; padding:2.5rem 1.5rem;">
        <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24"
             fill="none" stroke="#4b5563" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"
             style="margin-bottom:0.8rem;">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10 9 9 9 8 9"/>
        </svg>
        <div style="font-size:0.92rem; font-weight:500; color:#9ca3af; margin-bottom:0.3rem;">
            No results yet
        </div>
        <div style="font-size:0.82rem; color:#6b7280;">
            Enter a paragraph above, then click <strong>Recognize Tokens</strong> to begin.
        </div>
    </div>
    """, unsafe_allow_html=True)


# --------------- Footer ---------------
st.markdown("""
<div class="app-footer">
    CPT 411 Assignment 1  |  Prepared by: Ng Zi Jian, Khoo Kaa Hong, Axler Chin Shun Yuan  |  Scope: Number Data Finder (L2)
</div>
""", unsafe_allow_html=True)