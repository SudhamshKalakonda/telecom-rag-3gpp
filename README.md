
# 3GPP Telecom Standards RAG Assistant

RAG chatbot over 3GPP TS 23.501 (5G System Architecture), built for near-zero hallucination.

**Live demo:** https://telecom-rag-3gpp-genvlxnpmywtueaenzw3mp.streamlit.app/
**Repo:** https://github.com/SudhamshKalakonda/telecom-rag-3gpp

## How it works

PDF -> clause-aware chunking -> FastEmbed embeddings -> Pinecone -> retrieve top-k clauses -> LLM answers strictly from retrieved context -> a second LLM pass audits the answer for grounding -> Streamlit UI shows the answer with a grounded / refused status.

Two independent checks (self-refusal in the prompt, plus a separate grounding audit) both have to pass before an answer is shown as verified. Retrieved clauses and page numbers are shown in the UI for transparency.
