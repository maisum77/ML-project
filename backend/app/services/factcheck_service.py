from typing import Optional
from fact_check.verifier import verify_claim


async def fact_check_claim(claim: str):
    result = verify_claim(claim)
    return result
