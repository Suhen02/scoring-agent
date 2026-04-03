import json
import os
from typing import Dict
from dotenv import load_dotenv

from app.config import USE_MOCK_LLM, MAX_LLM_SCORE
from app.utils.logger import log
from app.llm.prompts import PROMPT

from langchain_groq import ChatGroq

load_dotenv()

os.environ['GROQ_API_KEY']=os.getenv('GROQ_API_KEY')

llm = ChatGroq(
    model="llama-3.3-70b-versatile",  
    temperature=0,             
    max_tokens=200
)

def safe_parse_json(text: str) -> Dict:
    try:
        return json.loads(text)
    except Exception:
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            return json.loads(text[start:end])
        except Exception:
            return {
                "score": 0,
                "is_generic": True,
                "ai_detected": True,
                "reason": "Failed to parse LLM output"
            }



def _mock_evaluate(candidate: dict) -> dict:
    answer = candidate.get("answer", "")

    if not answer:
        return {"score": 5, "is_generic": False, "ai_detected": False, "reason": "No answer"}

    score = 20
    reason = "Basic fallback"

    if len(answer) < 50:
        score = 10
        reason = "Short answer"

    if "comprehensive overview" in answer.lower():
        return {
            "score": 5,
            "is_generic": True,
            "ai_detected": True,
            "reason": "Generic AI phrase"
        }

    return {
        "score": min(score, MAX_LLM_SCORE),
        "is_generic": False,
        "ai_detected": False,
        "reason": reason,
    }



def evaluate_candidate(candidate: dict) -> dict:
    if USE_MOCK_LLM:
        log.info(f"[MOCK] {candidate['name']}")
        return _mock_evaluate(candidate)

    try:
        prompt = PROMPT.format(
            skills=", ".join(candidate.get("skills", [])) or "None",
            projects=candidate.get("projects", 0),
            github=candidate.get("github", "Not provided"),
            answer=candidate.get("answer", "No answer"),
        )

        response = llm.invoke(prompt)
        raw = response.content.strip()

        parsed = safe_parse_json(raw)

 
        score = max(0, min(int(parsed.get("score", 0)), MAX_LLM_SCORE))

        result = {
            "score": score,
            "is_generic": bool(parsed.get("is_generic", False)),
            "ai_detected": bool(parsed.get("ai_detected", False)),
            "reason": str(parsed.get("reason", "No reason")),
        }



        answer = candidate.get("answer", "").lower()

        # Rule-based override (very important)
        if "comprehensive overview" in answer:
            result["score"] = max(0, result["score"] - 10)
            result["is_generic"] = True
            result["ai_detected"] = True
            result["reason"] += " | Rule: generic phrase detected"

        log.info(
            f"[LLM] {candidate['name']} → {result['score']} "
            f"(Generic={result['is_generic']}, AI={result['ai_detected']})"
        )

        return result

    except Exception as e:
        log.error(f"[LLM ERROR] {candidate['name']}: {e}")
        return _mock_evaluate(candidate)