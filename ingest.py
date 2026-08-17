import os
import re
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document

# Load environment variables from .env file
load_dotenv()

INDEX_NAME = "telecom-rag"
# ... rest of your script

def clause_aware_split(pdf_path: str):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    
    # Clause pattern matching (e.g., "5.2.1", "4.1.3", "Annex A")
    clause_regex = re.compile(r'(\n(?:\d+\.){1,4}\d*\s+[A-Z][^\n]+)')
    
    documents = []
    current_clause = "General 3GPP Specs"
    
    for page in pages:
        text = page.page_content
        page_num = page.metadata.get("page", 0) + 1
        
        parts = clause_regex.split(text)
        
        for part in parts:
            if clause_regex.match(part):
                current_clause = part.strip()
            elif part.strip():
                doc = Document(
                    page_content=f"[Clause: {current_clause}]\n{part.strip()}",
                    metadata={
                        "source": "3GPP TS 23.501",
                        "clause": current_clause,
                        "page": page_num
                    }
                )
                documents.append(doc)
                
    return documents

def main():
    pdf_path = "./data/3gpp_ts_23501.pdf"
    if not os.path.exists(pdf_path):
        print("[-] PDF file not found. Run download_data.py first.")
        return

    print("[1/3] Parsing PDF with Clause-Aware Splitter...")
    docs = clause_aware_split(pdf_path)
    print(f"Total extracted clause chunks: {len(docs)}")

    print("[2/3] Initializing FastEmbed (384-dim BAAI/bge-small-en-v1.5)...")
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

    print("[3/3] Ingesting vector embeddings to Pinecone index 'telecom-rag'...")
    PineconeVectorStore.from_documents(
        documents=docs,
        embedding=embeddings,
        index_name=INDEX_NAME
    )
    print("[+] Ingestion Completed Successfully!")

if __name__ == "__main__":
    main()