from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

@tool("search_doctors")
def search_doctors(query: str) -> str:
    """Searches for suitable doctors based on specialty, location, or condition."""
    if not os.path.exists("./chroma_db"):
        return "Error: Doctor database not found. Please initialize the mock data."
        
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    
    docs = vectorstore.similarity_search(query, k=3)
    
    if not docs:
        return "No doctors found matching your criteria."
        
    results = "Here are the most suitable doctors I found:\n\n"
    for i, doc in enumerate(docs):
        results += f"Option {i+1}:\n"
        results += f"{doc.page_content}\n"
        results += f"Location: {doc.metadata.get('location', 'N/A')}\n\n"
        
    return results
