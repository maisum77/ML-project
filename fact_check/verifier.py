from fact_check.google_factcheck import google_fact_check
from fact_check.claimbuster import claimbuster_check


def verify_claim(claim: str) -> dict:
    checkworthiness = claimbuster_check(claim)

    if checkworthiness.get("checkworthy", False):
        fact_check = google_fact_check(claim)
    else:
        fact_check = {"verdict": "not_checkworthy", "claims": [], "confidence": 0}

    return {
        "claim": claim,
        "checkworthiness": checkworthiness,
        "fact_check": fact_check,
        "flagged": _is_flagged(fact_check),
    }


def _is_flagged(fact_check: dict) -> bool:
    verdict = fact_check.get("verdict", "").lower()
    flagged_verdicts = ["false", "mostly false", "mixture", "disputed", "unproven"]
    return any(v in verdict for v in flagged_verdicts)
