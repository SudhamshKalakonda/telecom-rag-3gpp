cat > README.md << 'EOF'

# 3GPP Telecom Standards RAG Assistant

RAG chatbot over 3GPP TS 23.501 (5G System Architecture), built for near-zero hallucination.

**Live demo:** _add Streamlit Cloud URL here_
**Repo:** https://github.com/SudhamshKalakonda/telecom-rag-3gpp

## How it works

PDF -> clause-aware chunking -> FastEmbed embeddings -> Pinecone -> retrieve top-k clauses -> LLM answers strictly from retrieved context -> a second LLM pass audits the answer for grounding -> Streamlit UI shows the answer with a grounded / refused status.

Two independent checks (self-refusal in the prompt, plus a separate grounding audit) both have to pass before an answer is shown as verified. Retrieved clauses and page numbers are shown in the UI for transparency.

## Setup

\`\`\`bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

Add a `.env` file (see `.env.example`) with `GROQ_API_KEY` and `PINECONE_API_KEY`.
Create a Pinecone index named `telecom-rag`, dimension 384, metric cosine.

## Run

\`\`\`bash
python download_data.py # fetch the 3GPP PDF
python ingest.py # chunk + embed + upsert to Pinecone
streamlit run app.py # launch the chat UI
\`\`\`

## Notes

- Scoped to a single spec (TS 23.501) — questions outside it are correctly refused rather than answered from general knowledge.
- The grounding audit adds a second LLM call per query, trading some latency for stronger hallucination protection.
  EOF
