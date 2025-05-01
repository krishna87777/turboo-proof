import google.generativeai as genai
import streamlit as st
from utils.github_scraper import search_github
from utils.arxiv_scraper import search_arxiv
from utils.vector_store import VectorStore

# Configure the Google Generative AI client using Streamlit secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

def generate_proof(topic):
    # Optional debug mode flag (optional in secrets)
    if st.secrets.get("DEBUG_MODE", "false").lower() == "true":
        return "DEBUG_MODE is enabled. No proof generated."

    # Step 1: Fetch documents
    github_results = search_github(topic)
    arxiv_results = search_arxiv(topic)

    # Step 2: Create and populate vector store
    vector_store = VectorStore()
    vector_store.add_documents(github_results + arxiv_results)

    # Step 3: Search for relevant docs
    relevant_docs = vector_store.search(topic, k=3)
    context = format_context(relevant_docs)

    # Step 4: Compose prompt
    prompt = f"""
    Topic: {topic}

    Reference Information:
    {context}

    Task: Generate a deep academic-level technical proof for the topic above.
    Use the reference information where relevant, but only if it's applicable.
    The proof should be thorough, well-structured, and include technical details.
    """

    # Step 5: Generate content with error handling
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating content: {e}"

def format_context(documents):
    """Formats document summaries into prompt context text."""
    context_parts = []
    for i, doc in enumerate(documents, 1):
        if "readme" in doc:
            context_parts.append(
                f"Source {i} (GitHub): {doc['title']}\n{doc['description']}\nExcerpt from README: {doc['readme'][:500]}...\n"
            )
        elif "summary" in doc:
            context_parts.append(
                f"Source {i} (arXiv): {doc['title']} by {doc['authors']}\nSummary: {doc['summary'][:500]}...\n"
            )
        else:
            context_parts.append(f"Source {i}: {str(doc)[:500]}...\n")
    return "\n".join(context_parts)
