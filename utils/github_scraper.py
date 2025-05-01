import requests
import base64
import time
import streamlit as st


def search_github(query, github_token=None, max_results=5):
    """
    Search GitHub repositories and fetch their details including README content.

    Args:
        query (str): The search query for repositories
        github_token (str): Optional GitHub API token for authentication
        max_results (int): Maximum number of results to return

    Returns:
        list: A list of dictionaries containing repository information
    """
    # Set up headers for API request
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    # Add token if provided (increases rate limits)
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    # Prepare search URL with query parameters
    search_url = f"https://api.github.com/search/repositories"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": max_results
    }

    try:
        # Make the search request
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Process results
        repos = response.json().get("items", [])
        results = []

        for repo in repos:
            # Get repository basic info
            repo_info = {
                "title": repo["name"],
                "full_name": repo["full_name"],
                "url": repo["html_url"],
                "description": repo["description"] or "No description available.",
                "stars": repo["stargazers_count"],
                "language": repo["language"],
                "owner": repo["owner"]["login"],
                "created_at": repo["created_at"],
                "readme": "No README found."
            }

            # Try to fetch README content
            try:
                # Rate limiting - add small delay between requests
                time.sleep(0.5)

                # Try main branch first (either master or main)
                for branch in ["master", "main"]:
                    readme_url = f"https://api.github.com/repos/{repo['full_name']}/contents/README.md?ref={branch}"
                    readme_response = requests.get(readme_url, headers=headers)

                    if readme_response.status_code == 200:
                        # README found, decode content
                        readme_data = readme_response.json()
                        if readme_data.get("content") and readme_data.get("encoding") == "base64":
                            readme_content = base64.b64decode(readme_data["content"]).decode('utf-8', errors='replace')
                            repo_info["readme"] = readme_content
                            break
            except Exception as e:
                # If README fetch fails, continue with default message
                pass

            results.append(repo_info)

        return results

    except Exception as e:
        st.error(f"Error searching GitHub: {str(e)}")
        return []


def get_repo_contents(repo_name, path="", github_token=None):
    """
    Get contents of a directory in a GitHub repository.

    Args:
        repo_name (str): Full repository name (owner/repo)
        path (str): Path within the repository
        github_token (str): GitHub API token

    Returns:
        list: Contents of the directory
    """
    headers = {"Accept": "application/vnd.github.v3+json"}
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    url = f"https://api.github.com/repos/{repo_name}/contents/{path}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching repo contents: {str(e)}")
        return []