import google.generativeai as genai
import os
from dotenv import load_dotenv
from utils.github_scraper import search_github
from utils.arxiv_scraper import search_arxiv
from utils.vector_store import VectorStore

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_proof(topic):
    github_results = search_github(topic)
    arxiv_results = search_arxiv(topic)

    vector_store = VectorStore()
    vector_store.add_documents(github_results + arxiv_results)

    relevant_docs = vector_store.search(topic, k=3)
    context = format_context(relevant_docs)

    prompt = f"""
    Topic: {topic}

    Reference Information:
    {context}

    Task: Generate a deep academic level technical proof for the topic above.
    Use the reference information where relevant, but only if it's applicable.
    The proof should be thorough, well-structured, and include technical details.
    """

    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    response = model.generate_content(prompt)

    return response.text

def format_context(documents):
    context_parts = []
    for i, doc in enumerate(documents, 1):
        if "readme" in doc:
            context_parts.append(
                f"Source {i} (GitHub): {doc['title']}\n{doc['description']}\nExcerpt from README: {doc['readme'][:500]}...\n")
        elif "summary" in doc:
            context_parts.append(
                f"Source {i} (arXiv): {doc['title']} by {doc['authors']}\nSummary: {doc['summary'][:500]}...\n")
        else:
            context_parts.append(f"Source {i}: {str(doc)[:500]}...\n")
    return "\n".join(context_parts)
