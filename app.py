import os
import streamlit as st
from dotenv import load_dotenv

# Page config MUST be the first Streamlit command
st.set_page_config(
    page_title="3GPP Telecom RAG",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load environment variables from local .env file
load_dotenv()

# Safely check Streamlit Cloud secrets vs local .env variables
def load_api_keys():
    try:
        if "PINECONE_API_KEY" in st.secrets:
            os.environ["PINECONE_API_KEY"] = st.secrets["PINECONE_API_KEY"]
        if "GROQ_API_KEY" in st.secrets:
            os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
    except Exception:
        # Fallback to local .env if secrets.toml does not exist
        pass

load_api_keys()

if not os.getenv("PINECONE_API_KEY") or not os.getenv("GROQ_API_KEY"):
    st.error("⚠️ **Missing API Keys!** Please check that `PINECONE_API_KEY` and `GROQ_API_KEY` are set in your `.env` file.")
    st.stop()

# Import rag_engine AFTER setting environment variables
from rag_engine import query_telecom_rag

# ----------------------------------------------------------------------------
# Styling — clean dark theme, generous type scale, sidebar toggle kept intact
# ----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hide only the menu/footer, NOT the header bar — the sidebar toggle
       lives in the header, hiding it entirely traps the sidebar closed. */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stDecoration"] { display: none; }
    header[data-testid="stHeader"] { background: transparent; }

    .stApp { background: #1e1e1e; }

    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 6rem;
        max-width: 820px;
    }

    /* Header */
    .app-header { margin-bottom: 2.4rem; }
    .app-header h1 {
        color: #f5f5f5;
        font-size: 2.1rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.01em;
    }
    .app-header p {
        color: #9b9b9b;
        font-size: 1.05rem;
        margin: 0;
        line-height: 1.5;
    }
    .assignment-tag {
        display: inline-block;
        margin-top: 0.9rem;
        font-size: 0.78rem;
        font-weight: 600;
        color: #f5c451;
        background: rgba(245, 196, 81, 0.1);
        border: 1px solid rgba(245, 196, 81, 0.3);
        padding: 0.3rem 0.75rem;
        border-radius: 6px;
        letter-spacing: 0.02em;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        background: transparent;
        padding: 0.55rem 0;
        border: none;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        display: flex;
        justify-content: flex-end;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
        background: #333333;
        border-radius: 18px;
        padding: 0.7rem 1.15rem;
        max-width: 75%;
        color: #f0f0f0;
        font-size: 1rem;
    }
    /* No avatars at all — plain bubble-on-right / plain-text-on-left, like ChatGPT */
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"],
    [data-testid="chatAvatarIcon-user"],
    [data-testid="chatAvatarIcon-assistant"] {
        display: none !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
        color: #e2e2e2;
        font-size: 1.05rem;
        line-height: 1.7;
    }

    /* Status line */
    .status-line {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        font-size: 0.88rem;
        color: #a0a0a0;
        margin: 0.7rem 0 0.5rem 0;
    }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
    .dot-grounded { background: #22c55e; }
    .dot-refused { background: #f59e0b; }

    /* Clause list */
    .clause-item { border-top: 1px solid #333333; padding: 0.8rem 0; }
    .clause-item:first-child { border-top: none; }
    .clause-meta {
        font-family: 'SF Mono', 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #808080;
        margin-bottom: 0.35rem;
        letter-spacing: 0.02em;
    }
    .clause-text { font-size: 0.9rem; color: #b8b8b8; line-height: 1.55; white-space: pre-wrap; }

    [data-testid="stExpander"] { border: none; background: transparent; }
    [data-testid="stExpander"] summary { color: #a0a0a0; font-size: 0.9rem; }

    /* Input bar */
    [data-testid="stChatInput"] textarea {
        background: #2b2b2b !important;
        border: 1px solid #4a4a4a !important;
        border-radius: 24px !important;
        color: #f0f0f0 !important;
        font-size: 1rem !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #171717;
        border-right: 1px solid #333333;
    }
    .sb-title { color: #f0f0f0; font-weight: 600; font-size: 1rem; margin: 0.2rem 0 0.7rem 0; }
    .sb-text { color: #9b9b9b; font-size: 0.92rem; line-height: 1.55; }
    .sb-example {
        color: #dcdcdc;
        font-size: 0.88rem;
        padding: 0.6rem 0.7rem;
        border-radius: 8px;
        margin-bottom: 0.35rem;
        border: 1px solid #333333;
    }
    .sb-divider { border-top: 1px solid #333333; margin: 1.2rem 0; }
    .sb-footer {
        font-size: 0.78rem;
        color: #6e6e6e;
        margin-top: 2rem;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sb-title">About</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sb-text">Answers are generated strictly from retrieved '
        'clauses of 3GPP TS 23.501 (5G System Architecture). If the spec '
        "doesn't cover a question, the assistant refuses rather than "
        'guessing.</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-title">Try asking</div>', unsafe_allow_html=True)
    for ex in [
        "What is the role of the AMF in the 5G System architecture?",
        "What is the function of the NSSF in network slice selection?",
        "How does the UE register with the network?",
    ]:
        st.markdown(f'<div class="sb-example">{ex}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-title">Stack</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sb-text">LangChain LCEL · Pinecone · Groq (Llama 3.3 70B) '
        "· FastEmbed · dual-pass grounding check</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sb-footer">Built as a Graduate Engineer Trainee '
        "assignment submission — demonstrates clause-aware RAG with "
        "a zero-hallucination guardrail.</div>",
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.markdown("""
<div class="app-header">
    <h1>3GPP Telecom Standards Assistant</h1>
    <p>Retrieval-augmented Q&A over 5G System Architecture (TS 23.501), guarded against hallucination.</p>
    <div class="assignment-tag">Built for Mavenir · Graduate Engineer Trainee Assignment</div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Chat state + history
# ----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

query = st.chat_input("Message the 3GPP assistant...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Searching 3GPP clauses & auditing response..."):
            ans, docs, status = query_telecom_rag(query)
            st.markdown(ans)

            if status == "VERIFIED_GROUNDED":
                st.markdown(
                    '<div class="status-line"><span class="status-dot dot-grounded"></span>'
                    "Grounded — backed by retrieved 3GPP clauses</div>",
                    unsafe_allow_html=True,
                )
            elif status in ["REFUSED", "FAILED_GROUNDING"]:
                st.markdown(
                    '<div class="status-line"><span class="status-dot dot-refused"></span>'
                    "Refused — insufficient or ungrounded context</div>",
                    unsafe_allow_html=True,
                )

            with st.expander("View retrieved clauses"):
                for doc in docs:
                    clause = doc.metadata.get("clause")
                    page = doc.metadata.get("page")
                    st.markdown(
                        f"""
                        <div class="clause-item">
                            <div class="clause-meta">CLAUSE {clause} · PAGE {page}</div>
                            <div class="clause-text">{doc.page_content}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    st.session_state.messages.append({"role": "assistant", "content": ans})