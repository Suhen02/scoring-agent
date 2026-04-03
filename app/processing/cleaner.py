
import re
from typing import Any, Optional

from app.utils.logger import log


def clean_text(value: Any) -> str:

    if value is None or (isinstance(value, float) and str(value) == "nan"):
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def clean_name(value: Any) -> str:
    if value is None or (isinstance(value, float) and str(value) == "nan"):
        return "Unknown"
    return str(value).strip().title()


def parse_skills(raw: Any) -> list[str]:
    text = clean_text(raw)
    if not text:
        return []
    # Split on common delimiters
    skills = re.split(r"[,;|/]+", text)
    return [s.strip() for s in skills if s.strip()]


def parse_projects_count(raw: Any) -> int:
  
    if raw is None or (isinstance(raw, float) and str(raw) == "nan"):
        return 0
    text = str(raw).strip()
    

    try:
        return max(0, int(float(text)))
    except (ValueError, TypeError):
        pass

    items = [i.strip() for i in re.split(r"[,;|]+", text) if i.strip()]
    return len(items)


def clean_github_url(raw: Any) -> Optional[str]:
    text = clean_text(raw)
    if not text or text in ("nan", "none", "n/a", "-", ""):
        return None
    
    if "github.com" not in text:
        if re.match(r"^[a-zA-Z0-9_-]+$", text.strip()):
            return f"https://github.com/{text.strip()}"
        return None
    
    if not text.startswith("http"):
        text = "https://" + text
    
    return text


def clean_answer(raw: Any) -> str:

    if raw is None or (isinstance(raw, float) and str(raw) == "nan"):
        return ""
    return str(raw).strip()


def clean_candidate(row: dict) -> dict:
   
    cleaned = {
        "name": clean_name(row.get("name")),
        "skills": parse_skills(row.get("skills")),
        "github": clean_github_url(row.get("github")),
        "projects": parse_projects_count(row.get("projects")),
        "answer": clean_answer(row.get("answer")),
        "_raw": row,
    }
    log.debug(f"Cleaned candidate: {cleaned['name']}")
    return cleaned
