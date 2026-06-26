import httpx
from typing import Any, Dict, List, Optional
from utils.logger import get_logger

logger = get_logger("service.github")

async def get_github_profile_data(username: str) -> Dict[str, Any]:
    """
    Fetch public repositories and user details for a GitHub username.
    Returns:
        {
            "username": str,
            "public_repos_count": int,
            "followers": int,
            "languages": List[str],
            "topics": List[str],
            "repo_summaries": List[Dict[str, Any]],
            "stats": Dict[str, Any]
        }
    """
    if not username:
        return {}

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "CommuneOS-App"
    }

    user_url = f"https://api.github.com/users/{username}"
    repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"

    data = {
        "username": username,
        "public_repos_count": 0,
        "followers": 0,
        "languages": [],
        "topics": [],
        "repo_summaries": [],
        "stats": {
            "total_stars": 0,
            "total_forks": 0
        }
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # 1. Fetch User Profile
            user_res = await client.get(user_url, headers=headers)
            if user_res.status_code == 200:
                user_info = user_res.json()
                data["public_repos_count"] = user_info.get("public_repos", 0)
                data["followers"] = user_info.get("followers", 0)
            elif user_res.status_code == 403:
                logger.warning(f"GitHub API rate limit hit when querying user {username}")
            else:
                logger.warning(f"Failed to fetch GitHub profile for {username}: {user_res.status_code}")

            # 2. Fetch User Repositories
            repos_res = await client.get(repos_url, headers=headers)
            if repos_res.status_code == 200:
                repos = repos_res.json()
                languages_set = set()
                topics_set = set()
                total_stars = 0
                total_forks = 0

                for repo in repos:
                    if repo.get("fork"):
                        continue
                    
                    lang = repo.get("language")
                    if lang:
                        languages_set.add(lang)

                    topics = repo.get("topics", [])
                    for topic in topics:
                        topics_set.add(topic)

                    stars = repo.get("stargazers_count", 0)
                    forks = repo.get("forks_count", 0)
                    total_stars += stars
                    total_forks += forks

                    data["repo_summaries"].append({
                        "name": repo.get("name"),
                        "description": repo.get("description"),
                        "language": lang,
                        "topics": topics,
                        "stars": stars,
                        "forks": forks
                    })

                data["languages"] = list(languages_set)
                data["topics"] = list(topics_set)
                data["stats"]["total_stars"] = total_stars
                data["stats"]["total_forks"] = total_forks

            elif repos_res.status_code == 403:
                logger.warning(f"GitHub API rate limit hit when querying repos for {username}")
            else:
                logger.warning(f"Failed to fetch GitHub repos for {username}: {repos_res.status_code}")

        except Exception as e:
            logger.error(f"GitHub service encountered an error for {username}: {e}", exc_info=True)

    return data
