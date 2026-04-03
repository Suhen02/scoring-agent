

from app.config import (
    SKILL_SCORES, MAX_SKILL_SCORE,
    PROJECT_THRESHOLD_HIGH, PROJECT_SCORE_HIGH, PROJECT_SCORE_LOW,
    GITHUB_MISSING_PENALTY, GITHUB_INVALID_PENALTY, GITHUB_EMPTY_PENALTY,
    GENERIC_PHRASES, GENERIC_PENALTY,
    MAX_RULE_SCORE,
)
from app.scoring.github_checker import check_github_profile
from app.utils.logger import log




def score_skills(skills) -> tuple[int, list[str]]:
    score = 0
    reasons = []
    matched = set()

    if not skills:
        return 0, ["No skills listed: +0"]

    for skill in skills:
        skill = str(skill).lower()

        for keyword, points in SKILL_SCORES.items():
            if keyword in skill and keyword not in matched:
                score += points
                matched.add(keyword)
                reasons.append(f"Skill '{keyword}': +{points}")

    score = min(score, MAX_SKILL_SCORE)
    return score, reasons



def score_projects(count) -> tuple[int, list[str]]:
    try:
        count = int(count or 0)
    except:
        count = 0

    if count >= PROJECT_THRESHOLD_HIGH:
        return PROJECT_SCORE_HIGH, [f"{count} projects (strong): +{PROJECT_SCORE_HIGH}"]

    return PROJECT_SCORE_LOW, [f"{count} projects (low): {PROJECT_SCORE_LOW}"]




def score_github(github_url) -> tuple[int, list[str]]:
    result = check_github_profile(github_url)
    status = result["status"]
    detail = result["details"]

    score_map = {
        "missing": (GITHUB_MISSING_PENALTY, "GitHub missing"),
        "invalid": (GITHUB_INVALID_PENALTY, f"GitHub invalid ({detail})"),
        "empty": (GITHUB_EMPTY_PENALTY, "GitHub empty profile"),
        "weak": (5, f"Weak GitHub ({detail})"),        
        "strong": (20, f"Strong GitHub ({detail})"),  
    }

    score, reason = score_map.get(status, (0, f"Unknown GitHub status: {status}"))

    return score, [f"{reason}: {score:+}"]



def detect_generic_answer(answer: str) -> tuple[int, list[str]]:
    if not answer:
        return -10, ["No answer provided: -10"]

    answer_lower = answer.lower()
    reasons = []
    penalty = 0

    # 1. Known AI phrases
    found = [p for p in GENERIC_PHRASES if p in answer_lower]
    if found:
        penalty += GENERIC_PENALTY
        reasons.append(f"AI phrases detected ({', '.join(found)}): {GENERIC_PENALTY}")

    # 2. Too short answers
    word_count = len(answer.split())
    if word_count < 5:
        penalty -= 10
        reasons.append("Very short answer: -10")

    # 3. Lack of action words (weak reasoning)
    action_words = ["built", "used", "implemented", "designed"]
    if not any(w in answer_lower for w in action_words):
        penalty -= 5
        reasons.append("No practical keywords detected: -5")

    if not reasons:
        return 0, ["Answer appears meaningful: +0"]

    return penalty, reasons



# Main Rule Score

def compute_rule_score(candidate: dict) -> tuple[int, list[str]]:
    total = 0
    all_reasons = []

    # Safe extraction (messy data handling )
    name = candidate.get("name", "Unknown")
    skills = candidate.get("skills") or []
    projects = candidate.get("projects", 0)
    github = candidate.get("github")
    answer = candidate.get("answer", "")

    log.info(f"[RULE] Processing {name}")

    components = [
        score_skills(skills),
        score_projects(projects),
        score_github(github),
        detect_generic_answer(answer),
    ]

    for score, reasons in components:
        total += score
        all_reasons.extend(reasons)

    total = max(0, min(total, MAX_RULE_SCORE))

    log.info(f"[RULE] {name} → Score: {total}")

    return total, all_reasons