import requests
import base64
import time
import streamlit as st

# Get GitHub token from Streamlit secrets (no error if missing)
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", None)

def search_github(query, github_token=GITHUB_TOKEN, max_results=5):
    """
    Search GitHub repositories and fetch details including README content.
    """
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    # Only add Authorization header if token is available
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

        # Silently ignore if unauthorized
        if response.status_code == 401:
            return []

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
            except Exception:
                pass  # Ignore README errors silently

            results.append(repo_info)

        return results

    except Exception:
        return []  # Silently fail on other exceptions


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
        if response.status_code == 401:
            return []  # Silent fail
        response.raise_for_status()
        return response.json()
    except Exception:
        return []  # Silent fail
