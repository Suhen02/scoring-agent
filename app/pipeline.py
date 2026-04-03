
import csv
import time
import json
from pathlib import Path

from app.config import RULE_WEIGHT, LLM_WEIGHT, TIERS
from app.processing.cleaner import clean_candidate
from app.processing.validator import validate_columns, validate_candidate
from app.scoring.rule_engine import compute_rule_score
from app.llm.evaluator import evaluate_candidate
from app.utils.logger import log



# Tier Classification
def classify_tier(score: float) -> str:
    for threshold, tier in TIERS:
        if score >= threshold:
            return tier
    return "Reject"


def load_candidates(csv_path: str) -> list[dict]:
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []

        col_map = {c.strip().lower(): c for c in columns}

        valid, warnings = validate_columns(list(col_map.keys()))
        for w in warnings:
            log.warning(f"[CSV WARNING] {w}")

        if not valid:
            raise ValueError(f"Invalid CSV structure: {warnings}")

        candidates = []
        for i, row in enumerate(reader):
            normalized = {k.strip().lower(): v for k, v in row.items()}
            candidates.append(normalized)

        log.info(f"[LOAD] Loaded {len(candidates)} candidates")

        return candidates


def process_candidate(raw: dict) -> dict:
    start_time = time.time()


    candidate = clean_candidate(raw)

    valid, warning = validate_candidate(candidate)
    if warning:
        log.warning(f"[VALIDATION] {candidate['name']}: {warning}")

    name = candidate.get("name", "Unknown")

    rule_start = time.time()
    rule_score, rule_reasons = compute_rule_score(candidate)
    rule_time = round((time.time() - rule_start) * 1000, 2)

    llm_start = time.time()
    llm_result = evaluate_candidate(candidate)
    llm_time = round((time.time() - llm_start) * 1000, 2)



    llm_score = llm_result["score"]

    llm_score_scaled = (llm_score / 40) * 100

    llm_reasons = [f"LLM: {llm_result.get('reason', '')}"]

    if llm_result.get("is_generic"):
        llm_reasons.append("LLM flagged generic answer")

    if llm_result.get("ai_detected"):
        llm_reasons.append("LLM flagged AI-generated content")

    final_score = round(
        (RULE_WEIGHT * rule_score) +
        (LLM_WEIGHT * llm_score_scaled),
        1
    )
    if final_score >= 60:
        final_score += 3

    tier = classify_tier(final_score)

    diff = abs(rule_score - llm_score_scaled)

    if diff > 20:
        confidence = "Low"
    elif diff > 10:
        confidence = "Medium"
    else:
        confidence = "High"

    reasons = {
        "rule": rule_reasons,
        "llm": llm_reasons,
    }

    total_time = round((time.time() - start_time) * 1000, 2)

    log.info(
        f"[PIPELINE] {name} → Final={final_score} "
        f"(Rule={rule_score}, LLM={llm_score}) "
        f"[{confidence}] "
        f"[{total_time}ms]"
    )

    return {
        "name": name,
        "final_score": final_score,
        "rule_score": rule_score,
        "llm_score": llm_score,
        "tier": tier,
        "confidence": confidence,
        "processing_time_ms": total_time,
        "rule_time_ms": rule_time,
        "llm_time_ms": llm_time,
        "reasons": json.dumps(reasons),
    }


def run_pipeline(input_csv: str, output_csv: str) -> list[dict]:
    log.info("=" * 60)
    log.info("CANDIDATE INTELLIGENCE PIPELINE STARTED")
    log.info("=" * 60)

    start = time.time()

    raw_candidates = load_candidates(input_csv)

    results = []

    for i, raw in enumerate(raw_candidates, 1):
        name = raw.get("name", f"Candidate {i}")
        log.info(f"[PROCESS] {i}/{len(raw_candidates)} → {name}")

        try:
            result = process_candidate(raw)
            results.append(result)

        except Exception as e:
            log.error(f"[ERROR] Failed for {name}: {e}")

            results.append({
                "name": name,
                "final_score": 0,
                "rule_score": 0,
                "llm_score": 0,
                "tier": "Reject",
                "confidence": "Low",
                "processing_time_ms": 0,
                "rule_time_ms": 0,
                "llm_time_ms": 0,
                "reasons": json.dumps({"error": str(e)}),
            })


    results.sort(key=lambda x: x["final_score"], reverse=True)

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "name",
        "final_score",
        "rule_score",
        "llm_score",
        "tier",
        "confidence",
        "processing_time_ms",
        "rule_time_ms",
        "llm_time_ms",
        "reasons",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    elapsed = round(time.time() - start, 2)

    log.info(f"Pipeline completed in {elapsed}s")
    log.info(f"Output saved to: {output_csv}")
    log.info(f"Tier Summary: {_tier_summary(results)}")

    return results


def _tier_summary(results: list[dict]) -> str:
    counts = {}

    for r in results:
        tier = r["tier"]
        counts[tier] = counts.get(tier, 0) + 1

    return ", ".join(f"{tier}: {count}" for tier, count in sorted(counts.items()))