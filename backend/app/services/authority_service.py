"""
Authority verification service: checks if a source is credible/official
and calculates an authority score 0-100.
"""

from typing import Dict, Optional
from backend.app.models.authority_sources import (
    is_authoritative_handle,
    is_authoritative_subreddit,
    is_authoritative_domain,
    get_source_type,
    get_authority_score,
)


async def check_authority(author: str, platform: str = "twitter",
                          verified: bool = False, subreddit: str = None,
                          url: str = None) -> Dict:
    if not author:
        return {
            "author": author,
            "verified": verified,
            "authority_score": 0,
            "author_type": "public",
            "is_authentic": False,
            "reason": "No author information available",
        }

    source_type = get_source_type(author, platform, subreddit, url)
    score = get_authority_score(author, platform, verified, subreddit, url)

    reasons = []
    if source_type == "official":
        reasons.append(f"@{author} is a recognized official source")
    elif source_type == "org":
        reasons.append(f"@{author} is a recognized organization")
    elif source_type == "journalist":
        reasons.append(f"@{author} appears to be a news/media source")
    if verified:
        reasons.append(f"Account is platform-verified")
    if is_authoritative_domain(url):
        reasons.append(f"URL domain is from an authoritative source")

    return {
        "author": author,
        "platform": platform,
        "verified": verified,
        "authority_score": score,
        "author_type": source_type,
        "is_authentic": score >= 60,
        "reasons": reasons if reasons else ["No special authority signals detected"],
    }


async def check_post_authority(post: Dict) -> Dict:
    if not post:
        return {"authority_score": 0, "author_type": "public", "is_authentic": False}

    author = post.get("author", "")
    platform = post.get("platform", "twitter")
    verified = post.get("author_verified", False)
    subreddit = post.get("subreddit")
    url = post.get("url")

    return await check_authority(author, platform, verified, subreddit, url)
