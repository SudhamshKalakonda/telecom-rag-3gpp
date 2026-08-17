import os
import streamlit as st
from dotenv import load_dotenv

# Page config MUST be the first Streamlit command
st.set_page_config(page_title="3GPP Telecom RAG", page_icon="📡", layout="wide")

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

st.title("📡 3GPP Telecom Standards AI Assistant")
st.caption("Powered by LangChain, FastEmbed, Pinecone, and Groq | Zero-Hallucination Guarded")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

query = st.chat_input("Ask a 3GPP specification question (e.g., What is the role of NSSF in selecting network slice instances?)...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
        
    with st.chat_message("assistant"):
        with st.spinner("Searching 3GPP Clauses & Auditing Response..."):
            ans, docs, status = query_telecom_rag(query)
            st.markdown(ans)
            
            if status == "VERIFIED_GROUNDED":
                st.success("✅ Grounding Check Passed: Answer strictly backed by 3GPP context.")
            elif status in ["REFUSED", "FAILED_GROUNDING"]:
                st.warning("⚠️ Hallucination Guard Triggered: Insufficient/ungrounded context.")
                
            with st.expander("🔍 View Retrieved 3GPP Clauses & Metadata"):
                for doc in docs:
                    st.write(f"**Clause:** `{doc.metadata.get('clause')}` | **Page:** `{doc.metadata.get('page')}`")
                    st.text(doc.page_content)
                    st.divider()
                    
    st.session_state.messages.append({"role": "assistant", "content": ans})