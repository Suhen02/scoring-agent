
RULE_WEIGHT = 0.45
LLM_WEIGHT = 0.55

SKILL_SCORES = {
    "python": 12,
    "ml": 8,
    "ai": 8,
    "machine learning": 8,
    "artificial intelligence": 8,
    "deep learning": 8,
    "tensorflow": 4,
    "pytorch": 4,
    "pandas": 4,
    "numpy": 4,
    "scikit-learn": 4,
    "sql": 4,
    "docker": 4,
    "javascript": 4,
    "react": 4,
}

MAX_SKILL_SCORE = 25   

PROJECT_THRESHOLD_HIGH = 3
PROJECT_SCORE_HIGH = 15
PROJECT_SCORE_LOW = -3   


GITHUB_MISSING_PENALTY = -8
GITHUB_INVALID_PENALTY = -10
GITHUB_EMPTY_PENALTY = -5
GITHUB_VALID_SCORE = 10


GENERIC_PHRASES = [
    "comprehensive overview",
    "rapidly evolving",
    "i'd be happy to help",
    "i would be happy to help",
    "in today's fast-paced",
    "leverage my skills",
    "passionate about technology",
    "dynamic environment",
    "synergy",
    "paradigm shift",
]

GENERIC_PENALTY = -10  

TIERS = [
    (60, "Fast-Track"), 
    (50, "Standard"),
    (35, "Review"),
    (0, "Reject"),
]

GITHUB_TIMEOUT = 5
GITHUB_MAX_RETRIES = 2
GITHUB_RETRY_DELAY = 1

LLM_MODEL = "mixtral-8x7b-32768"  
USE_MOCK_LLM = False


MAX_RULE_SCORE = 100
MAX_LLM_SCORE = 40