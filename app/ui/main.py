import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from app.core.config import config
from app.core.logging_config import write_audit_event
from app.services.bot_service import SQLBotService


st.set_page_config(
    page_title="Enterprise SQL Assistant",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_enterprise_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --app-bg: #f5f7fb;
                --panel-bg: #ffffff;
                --ink: #172033;
                --muted: #637083;
                --line: #d9e0ea;
                --accent: #1f5eff;
            }

            .stApp {
                background: var(--app-bg);
                color: var(--ink);
            }

            .block-container {
                padding-top: 1.35rem;
                padding-bottom: 5.5rem;
                max-width: 1180px;
            }

            [data-testid="stSidebar"] {
                background: #101827;
                border-right: 1px solid #1f2b3d;
            }

            [data-testid="stSidebar"] * {
                color: #eef4ff;
            }

            [data-testid="stSidebar"] .stSelectbox label,
            [data-testid="stSidebar"] .stCaptionContainer {
                color: #b8c4d6;
            }

            [data-testid="stSidebar"] div[data-baseweb="select"] > div {
                background: #172236;
                border-color: #334155;
                border-radius: 8px;
            }

            .app-header {
                background: var(--panel-bg);
                border: 1px solid var(--line);
                border-radius: 8px;
                padding: 22px 24px;
                box-shadow: 0 10px 28px rgba(23, 32, 51, 0.06);
                margin-bottom: 18px;
            }

            .eyebrow {
                color: var(--accent);
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0;
                text-transform: uppercase;
                margin-bottom: 6px;
            }

            .app-title {
                color: var(--ink);
                font-size: 2rem;
                line-height: 1.15;
                font-weight: 760;
                margin: 0;
            }

            .app-subtitle {
                color: var(--muted);
                font-size: 0.98rem;
                line-height: 1.55;
                margin-top: 8px;
                max-width: 760px;
            }

            .status-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 12px;
                margin: 8px 0 18px;
            }

            .status-card {
                background: var(--panel-bg);
                border: 1px solid var(--line);
                border-radius: 8px;
                padding: 14px 16px;
                min-height: 86px;
            }

            .status-label {
                color: var(--muted);
                font-size: 0.78rem;
                font-weight: 650;
                margin-bottom: 6px;
            }

            .status-value {
                color: var(--ink);
                font-size: 0.98rem;
                font-weight: 720;
                overflow-wrap: anywhere;
            }

            .status-note {
                color: var(--muted);
                font-size: 0.75rem;
                margin-top: 5px;
            }

            .chat-shell {
                padding: 4px 0 0;
            }

            .section-title {
                color: var(--ink);
                font-size: 0.95rem;
                font-weight: 740;
                margin-bottom: 3px;
            }

            .section-caption {
                color: var(--muted);
                font-size: 0.82rem;
                margin-bottom: 10px;
            }

            .empty-state {
                border-left: 3px solid var(--line);
                padding: 8px 0 8px 12px;
                margin: 8px 0 10px;
                color: var(--muted);
                font-size: 0.86rem;
            }

            .sidebar-brand {
                font-size: 1.08rem;
                font-weight: 760;
                color: #ffffff;
                margin-bottom: 2px;
            }

            .sidebar-copy {
                font-size: 0.82rem;
                line-height: 1.45;
                color: #b8c4d6;
                margin-bottom: 18px;
            }

            .sidebar-panel {
                background: #172236;
                border: 1px solid #2a3850;
                border-radius: 8px;
                padding: 12px;
                margin: 12px 0;
            }

            .sidebar-panel-label {
                color: #93a4bb;
                font-size: 0.73rem;
                font-weight: 700;
                text-transform: uppercase;
                margin-bottom: 4px;
            }

            .sidebar-panel-value {
                color: #ffffff;
                font-size: 0.86rem;
                overflow-wrap: anywhere;
            }

            .stButton > button,
            .stDownloadButton > button {
                border-radius: 8px;
                border: 1px solid #2a3850;
                background: #172236;
                color: #eef4ff;
                font-weight: 650;
            }

            .stButton > button:hover,
            .stDownloadButton > button:hover {
                border-color: #6b8cff;
                color: #ffffff;
            }

            section.main .stButton > button {
                background: #ffffff;
                color: #243047;
                border: 1px solid var(--line);
                font-weight: 600;
                min-height: 2.35rem;
            }

            section.main .stButton > button:hover {
                color: var(--accent);
                border-color: #b9c8ff;
                background: #fbfcff;
            }

            div[data-testid="stChatInput"] {
                border-top: 1px solid var(--line);
                background: rgba(245, 247, 251, 0.95);
            }

            @media (max-width: 780px) {
                .status-grid {
                    grid-template-columns: 1fr;
                }

                .app-title {
                    font-size: 1.55rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner=False)
def get_bot(model_name: str) -> SQLBotService:
    return SQLBotService(model_name=model_name)


def set_pending_prompt(text: str) -> None:
    st.session_state.pending_prompt = text


def render_sidebar(model: str) -> None:
    db_info = config.effective_database_settings

    st.markdown(
        f"""
        <div class="sidebar-panel">
            <div class="sidebar-panel-label">Database</div>
            <div class="sidebar-panel-value">{db_info['server']} / {db_info['database']}</div>
        </div>
        <div class="sidebar-panel">
            <div class="sidebar-panel-label">Driver</div>
            <div class="sidebar-panel-value">{db_info['driver']}</div>
        </div>
        <div class="sidebar-panel">
            <div class="sidebar-panel-label">Qdrant Endpoint</div>
            <div class="sidebar-panel-value">{config.qdrant_url}</div>
        </div>
        <div class="sidebar-panel">
            <div class="sidebar-panel-label">Active Model</div>
            <div class="sidebar-panel-value">{model}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []

    audit_path = config.root_dir / "logs" / "app.csv"
    if audit_path.exists():
        with open(audit_path, "rb") as file:
            st.download_button(
                "Download Audit Logs",
                file,
                "app.csv",
                "text/csv",
                use_container_width=True,
            )
    else:
        st.caption("No audit log has been created yet.")


def render_header(model: str) -> None:
    db_info = config.effective_database_settings
    st.markdown(
        """
        <div class="app-header">
            <div class="eyebrow">Governed analytics bot</div>
            <h1 class="app-title">Ask business questions. Get database-backed answers.</h1>
            <div class="app-subtitle">
                Query SQL Server through a controlled assistant that retrieves approved schema context,
                validates generated SQL, executes read-only queries, and returns business-ready summaries.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="status-grid">
            <div class="status-card">
                <div class="status-label">SQL Server</div>
                <div class="status-value">{db_info['server']}</div>
                <div class="status-note">Windows Authentication</div>
            </div>
            <div class="status-card">
                <div class="status-label">Database</div>
                <div class="status-value">{db_info['database']}</div>
                <div class="status-note">Read-only query execution</div>
            </div>
            <div class="status-card">
                <div class="status-label">LLM Runtime</div>
                <div class="status-value">{model}</div>
                <div class="status-note">Ollama local model</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state() -> None:
    st.markdown(
        """
        <div class="empty-state">
            Start with a focused business question. The assistant keeps generated SQL internal and returns the result as a business answer.
        </div>
        """,
        unsafe_allow_html=True,
    )


def handle_prompt(prompt: str, model: str) -> None:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Querying database and preparing the answer..."):
            bot = get_bot(model_name=model)
            answer, generated_sql = bot.ask(prompt)
            st.markdown(answer)

            status = (
                "success"
                if generated_sql
                and not answer.startswith(
                    ("Execution Error", "Security Violation", "I could not generate")
                )
                else "failed"
            )
            write_audit_event(prompt, generated_sql, answer, status)

    st.session_state.messages.append({"role": "assistant", "content": answer})


inject_enterprise_styles()

if "messages" not in st.session_state:
    st.session_state.messages = []

configured_model = config.settings.get("ollama", {}).get("model", "llama3")
available_models = list(dict.fromkeys([configured_model, "llama3", "mistral"]))

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">Enterprise SQL Assistant</div>
        <div class="sidebar-copy">Natural language access to governed SQL Server insights.</div>
        """,
        unsafe_allow_html=True,
    )
    selected_model = st.selectbox("Ollama Model", available_models)
    render_sidebar(selected_model)

render_header(selected_model)

st.markdown('<div class="chat-shell">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Ask a Question</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">Use a sample prompt or type your own business question below.</div>',
    unsafe_allow_html=True,
)

if not st.session_state.messages:
    render_empty_state()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

typed_prompt = st.chat_input("Ask a business question...")
active_prompt = typed_prompt or st.session_state.pop("pending_prompt", None)

if active_prompt:
    handle_prompt(active_prompt, selected_model)

st.markdown("</div>", unsafe_allow_html=True)
