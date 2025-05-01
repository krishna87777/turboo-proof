import requests
import base64
import time
import streamlit as st


def search_github(query, github_token=None, max_results=5):
    """
    Search GitHub repositories and fetch details including README content.
    Uses public API without requiring authentication token.
    The github_token parameter is kept for backward compatibility but is no longer used.
    """
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    search_url = "https://api.github.com/search/repositories"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": max_results
    }

    try:
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        repos = response.json().get("items", [])
        results = []

        for repo in repos:
            repo_info = {
                "title": repo["name"],
                "full_name": repo["full_name"],
                "url": repo["html_url"],
                "description": repo.get("description") or "No description available.",
                "stars": repo["stargazers_count"],
                "language": repo["language"],
                "owner": repo["owner"]["login"],
                "created_at": repo["created_at"],
                "readme": "No README found."
            }

            # Try to fetch README from known branches
            try:
                time.sleep(1)  # Increased delay to respect rate limits for unauthenticated requests

                for branch in ["main", "master"]:
                    readme_url = f"https://api.github.com/repos/{repo['full_name']}/contents/README.md?ref={branch}"
                    readme_response = requests.get(readme_url, headers=headers)

                    if readme_response.status_code == 200:
                        readme_data = readme_response.json()
                        if readme_data.get("encoding") == "base64":
                            readme_content = base64.b64decode(readme_data["content"]).decode("utf-8", errors="replace")
                            repo_info["readme"] = readme_content
                            break
            except Exception:
                pass  # Ignore README errors silently

            results.append(repo_info)

        return results

    except Exception as e:
        st.error(f"Error searching GitHub: {e}")
        return []


def get_repo_contents(repo_name, path="", github_token=None):
    """
    Get the contents of a GitHub repository path without authentication.
    The github_token parameter is kept for backward compatibility but is no longer used.
    """
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    url = f"https://api.github.com/repos/{repo_name}/contents/{path}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching repo contents: {e}")
        return []


# Example Streamlit UI implementation
def github_search_app():
    st.title("GitHub Repository Search")

    query = st.text_input("Search for repositories:", "")
    max_results = st.slider("Maximum number of results:", 1, 10, 5)

    if st.button("Search") and query:
        with st.spinner("Searching GitHub..."):
            results = search_github(query, max_results=max_results)

        if results:
            st.success(f"Found {len(results)} repositories")
            for repo in results:
                with st.expander(f"{repo['title']} ({repo['stars']} ⭐)"):
                    st.markdown(f"**Description:** {repo['description']}")
                    st.markdown(f"**Language:** {repo['language'] or 'Not specified'}")
                    st.markdown(f"**Owner:** {repo['owner']}")
                    st.markdown(f"**URL:** [{repo['url']}]({repo['url']})")

                    if repo['readme'] != "No README found.":
                        with st.expander("View README"):
                            st.markdown(repo['readme'])
        else:
            st.warning("No repositories found for your search query.")

# Uncomment to run the app
# if __name__ == "__main__":
#     github_search_app()
