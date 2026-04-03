
import time
from typing import Optional, Dict

from app.config import GITHUB_TIMEOUT, GITHUB_MAX_RETRIES, GITHUB_RETRY_DELAY
from app.utils.logger import log

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def normalize_github_url(url: str) -> str:
    url = url.strip()
    if not url.startswith("http"):
        url = "https://" + url
    return url.rstrip("/")


def extract_username(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def check_github_profile(url: Optional[str]) -> Dict[str, str]:
 
    if not url:
        return {"status": "missing", "details": "No GitHub URL provided"}

    if "github.com" not in url:
        return {"status": "invalid", "details": f"Not a GitHub URL: {url}"}

    if not HAS_REQUESTS:
        log.warning("requests not installed, using simulated check")
        return _simulate_check(url)

    url = normalize_github_url(url)
    username = extract_username(url)

    api_url = f"https://api.github.com/users/{username}"

    for attempt in range(GITHUB_MAX_RETRIES + 1):
        try:
            log.info(f"Checking GitHub API for {username} (attempt {attempt + 1})")

            resp = requests.get(api_url, timeout=GITHUB_TIMEOUT)

            if resp.status_code == 404:
                return {"status": "invalid", "details": "User not found"}

            if resp.status_code == 429:
                log.warning("GitHub API rate limited")
                if attempt < GITHUB_MAX_RETRIES:
                    time.sleep(GITHUB_RETRY_DELAY * (attempt + 1))
                    continue
                return {"status": "weak", "details": "Rate limited, partial confidence"}

            if resp.status_code >= 400:
                return {"status": "invalid", "details": f"HTTP {resp.status_code}"}

            data = resp.json()

            public_repos = data.get("public_repos", 0)
            followers = data.get("followers", 0)

            log.info(f"{username}: repos={public_repos}, followers={followers}")


            if public_repos == 0:
                return {"status": "empty", "details": "No public repositories"}

            if public_repos < 3 and followers == 0:
                return {
                    "status": "weak",
                    "details": f"Low activity ({public_repos} repos, {followers} followers)"
                }

            return {
                "status": "strong",
                "details": f"{public_repos} repos, {followers} followers"
            }

        except requests.exceptions.Timeout:
            log.warning(f"Timeout for {username}, retrying...")
            if attempt < GITHUB_MAX_RETRIES:
                time.sleep(GITHUB_RETRY_DELAY)
                continue
            break

        except requests.exceptions.RequestException as e:
            log.warning(f"Request failed: {e}")
            break


    try:
        log.info(f"Falling back to HTML check for {url}")

        resp = requests.get(url, timeout=GITHUB_TIMEOUT)

        if resp.status_code == 404:
            return {"status": "invalid", "details": "Profile not found"}

        page_text = resp.text.lower()

        if "doesn't have any public repositories" in page_text or "0 repositories" in page_text:
            return {"status": "empty", "details": "No public repos (HTML check)"}

        return {"status": "weak", "details": "Profile exists (HTML fallback)"}

    except Exception as e:
        log.warning(f"Fallback failed: {e}")


    return {"status": "weak", "details": "Could not fully validate profile"}



def _simulate_check(url: str) -> Dict[str, str]:
    if "invalid" in url:
        return {"status": "invalid", "details": "Simulated invalid"}
    if "empty" in url:
        return {"status": "empty", "details": "Simulated empty"}
    if "weak" in url:
        return {"status": "weak", "details": "Simulated weak"}
    return {"status": "strong", "details": "Simulated strong"}