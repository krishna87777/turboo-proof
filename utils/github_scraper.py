import requests
import base64
import time
import streamlit as st

# Get GitHub token from Streamlit secrets
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")

def search_github(query, github_token=GITHUB_TOKEN, max_results=5):
    """
    Search GitHub repositories and fetch details including README content.
    """
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    if github_token:
        headers["Authorization"] = f"token {github_token}"

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
                time.sleep(0.5)  # Respect rate limits

                for branch in ["main", "master"]:
                    readme_url = f"https://api.github.com/repos/{repo['full_name']}/contents/README.md?ref={branch}"
                    readme_response = requests.get(readme_url, headers=headers)

                    if readme_response.status_code == 200:
                        readme_data = readme_response.json()
                        if readme_data.get("encoding") == "base64":
                            readme_content = base64.b64decode(readme_data["content"]).decode("utf-8", errors="replace")
                            repo_info["readme"] = readme_content
                            break
            except Exception as e:
                st.warning(f"Failed to fetch README for {repo['full_name']}: {e}")

            results.append(repo_info)

        return results

    except Exception as e:
        st.error(f"GitHub search failed: {str(e)}")
        return []

def get_repo_contents(repo_name, path="", github_token=GITHUB_TOKEN):
    """
    Get the contents of a GitHub repository path.
    """
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    url = f"https://api.github.com/repos/{repo_name}/contents/{path}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching contents from {repo_name}/{path}: {str(e)}")
        return []
