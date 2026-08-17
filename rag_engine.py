import os
from dotenv import load_dotenv

# MUST be at the very top to parse .env before initializing models
load_dotenv()

from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

INDEX_NAME = "telecom-rag"

# Fetch keys explicitly
groq_key = os.getenv("GROQ_API_KEY")
pinecone_key = os.getenv("PINECONE_API_KEY")

if not groq_key or not pinecone_key:
    raise ValueError("[-] GROQ_API_KEY or PINECONE_API_KEY missing from environment or .env file.")

# Initialize Embeddings
embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

# Initialize Pinecone Vector Store explicitly with api_key
vectorstore = PineconeVectorStore(
    index_name=INDEX_NAME, 
    embedding=embeddings,
    pinecone_api_key=pinecone_key
)

# k=4 retrieved clauses per query
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    groq_api_key=groq_key,
    temperature=0.0
)

SYSTEM_PROMPT = """You are a strict 3GPP Telecom Standards Assistant.

Answer the user's question relying ONLY and EXCLUSIVELY on the retrieved 3GPP clauses below.
Rules to enforce zero hallucinations:
1. If the retrieved context does not explicitly contain the answer, reply ONLY with:
   "I cannot answer based on the provided 3GPP standards context."
2. Cite the exact [Clause: X] in your response whenever citing a technical requirement.
3. Do NOT extrapolate or assume information not present in the clauses.

Retrieved Context:
{context}

User Question: {question}
Answer:"""

prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)

GROUNDING_CHECK_PROMPT = """You are an auditor verifying RAG responses.

Evaluate if the Answer relies ONLY on the provided Context. 
- If the answer accurately reflects facts in the Context (even if summarized), respond ONLY with "GROUNDED".
- Respond with "UNGROUNDED" ONLY if the answer makes major claims NOT found in the Context.

Context:
{context}

Answer:
{answer}

Verification Result:"""

eval_prompt = ChatPromptTemplate.from_template(GROUNDING_CHECK_PROMPT)

# --- LCEL chains ---
# Answer chain: retriever feeds {context}, question passes through, prompt -> llm -> string
def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

answer_chain = (
    prompt
    | llm
    | StrOutputParser()
)

# Grounding-audit chain: takes {context, answer} -> "GROUNDED" / "UNGROUNDED"
grounding_chain = (
    eval_prompt
    | llm
    | StrOutputParser()
)

REFUSAL_MESSAGE = "I cannot answer based on the provided 3GPP standards context."

def query_telecom_rag(query: str):
    docs = retriever.invoke(query)
    context_str = format_docs(docs)

    response = answer_chain.invoke({"context": context_str, "question": query})

    # Path 1: Model explicitly refused based on prompt instruction.
    # Even if the model hedges first and only appends the refusal phrase at
    # the end, treat it as a refusal and show the clean message — not the
    # rambling lead-up, which reads as a contradictory half-answer.
    if REFUSAL_MESSAGE in response:
        return REFUSAL_MESSAGE, docs, "REFUSED"

    eval_result = grounding_chain.invoke({"context": context_str, "answer": response}).strip()

    # Path 2: Audit check failed
    if "UNGROUNDED" in eval_result:
        return REFUSAL_MESSAGE, docs, "FAILED_GROUNDING"

    # Path 3: Audit check passed
    return response, docs, "VERIFIED_GROUNDED"

if __name__ == "__main__":
    print("--- 3GPP Telecom RAG Assistant Initialized ---")
    print("Type 'exit' or 'quit' to end.\n")
    
    while True:
        user_input = input("\nEnter 3GPP Query: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        if not user_input.strip():
            continue
            
        ans, docs, status = query_telecom_rag(user_input)
        print(f"[+] Status: {status}")
        print(f"[+] Answer:\n{ans}")