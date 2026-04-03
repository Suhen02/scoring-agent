

from typing import Optional

from app.utils.logger import log


REQUIRED_COLUMNS = {"name"}
EXPECTED_COLUMNS = {"name", "skills", "github", "projects", "answer"}


def validate_columns(columns: list[str]) -> tuple[bool, list[str]]:
  
    col_set = {c.strip().lower() for c in columns}
    warnings = []
    
    missing_required = REQUIRED_COLUMNS - col_set
    if missing_required:
        return False, [f"Missing required columns: {missing_required}"]
    
    missing_optional = EXPECTED_COLUMNS - col_set
    if missing_optional:
        warnings.append(f"Missing optional columns (will use defaults): {missing_optional}")
    
    extra = col_set - EXPECTED_COLUMNS
    if extra:
        warnings.append(f"Extra columns ignored: {extra}")
    
    return True, warnings


def validate_candidate(candidate: dict) -> tuple[bool, Optional[str]]:
  
    if not candidate.get("name") or candidate["name"] == "Unknown":
        log.warning("Candidate with missing name found")
        return True, "Missing name"  
    return True, None
