from fastapi import APIRouter, Query
from backend.app.services.authority_service import check_authority, check_post_authority
from backend.app.core.database import raw_posts_collection
from backend.app.models.authority_sources import OFFICIAL_TWITTER, OFFICIAL_REDDIT, AUTHORITY_DOMAINS

router = APIRouter()


@router.get("/check")
async def check(author: str = Query(...), platform: str = Query("twitter")):
    result = await check_authority(author=author, platform=platform)
    return result


@router.get("/post/{post_id}")
async def check_post(post_id: str):
    post = await raw_posts_collection.find_one({"id": post_id})
    if not post:
        return {"error": "Post not found"}
    result = await check_post_authority(post)
    return result


@router.get("/scorecard")
async def get_scorecard():
    official_sources = []
    for handle in sorted(OFFICIAL_TWITTER):
        source_type = "official"
        if any(w in handle for w in ["news", "press", "media", "times", "post", "daily", "chronicle", "gazette", "herald", "journal", "tribune"]):
            source_type = "journalist"
        official_sources.append({
            "handle": f"@{handle}",
            "platform": "twitter",
            "type": source_type,
            "authority_score": 95 if source_type == "official" else 80,
        })

    for handle in sorted(OFFICIAL_REDDIT):
        official_sources.append({
            "handle": f"u/{handle}",
            "platform": "reddit",
            "type": "official",
            "authority_score": 95,
        })

    domain_list = []
    for domain in sorted(AUTHORITY_DOMAINS):
        domain_type = "government" if domain.endswith((".gov", ".int")) else "academic" if domain.endswith((".edu", ".ac.uk")) else "organization"
        domain_list.append({
            "domain": domain,
            "type": domain_type,
        })

    type_counts = {}
    for s in official_sources:
        t = s["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    return {
        "total_sources": len(official_sources),
        "twitter_sources": len([s for s in official_sources if s["platform"] == "twitter"]),
        "reddit_sources": len([s for s in official_sources if s["platform"] == "reddit"]),
        "authority_domains": len(domain_list),
        "type_distribution": type_counts,
        "sources": official_sources,
        "domains": domain_list,
    }
