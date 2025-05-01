import arxiv
import streamlit as st
import time
from datetime import datetime


def search_arxiv(query, max_results=5):
    """
    Search arXiv for papers related to the query.

    Args:
        query (str): The search query for arXiv papers
        max_results (int): Maximum number of results to return

    Returns:
        list: A list of dictionaries containing paper information
    """
    try:
        # Configure arXiv search client
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        results = []

        # Process results
        for result in search.results():
            # Format authors list
            authors = ", ".join([author.name for author in result.authors])

            # Format publication date
            published_date = result.published.strftime('%Y-%m-%d') if result.published else "Unknown"

            # Generate a summary that's not too long
            summary = result.summary.replace("\n", " ")
            if len(summary) > 500:
                summary = summary[:500] + "..."

            # Create paper info dictionary
            paper_info = {
                "title": result.title,
                "summary": summary,
                "url": result.entry_id,
                "pdf_url": result.pdf_url,
                "authors": authors,
                "published": published_date,
                "categories": ", ".join(result.categories),
                "comment": result.comment if hasattr(result, 'comment') else None
            }

            results.append(paper_info)

            # Small delay to avoid overwhelming the service
            time.sleep(0.1)

        return results

    except Exception as e:
        st.error(f"Error searching arXiv: {str(e)}")
        return []


def format_arxiv_reference(paper):
    """
    Format an arXiv paper as an academic reference.

    Args:
        paper (dict): Paper information dictionary

    Returns:
        str: Formatted citation
    """
    try:
        # Extract year from published date
        year = "Unknown"
        if paper.get("published"):
            try:
                year = paper["published"].split("-")[0]
            except:
                pass

        citation = f"{paper['authors']} ({year}). {paper['title']}. arXiv preprint {paper['url'].split('/')[-1]}"
        return citation
    except:
        return f"{paper.get('title', 'Unknown paper')}. arXiv."