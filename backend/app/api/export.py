from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from typing import Optional
from backend.app.core.database import raw_posts_collection
from backend.app.services.clustering_service import get_topic_clusters
from backend.app.services.authority_service import get_source_type

router = APIRouter()


@router.get("/")
async def export_data(
    format: str = Query("json", pattern="^(json|csv)$"),
    platform: Optional[str] = Query(None),
    limit: int = Query(1000),
):
    query = {}
    if platform:
        query["platform"] = platform

    cursor = (await raw_posts_collection.find(query)).limit(limit)
    posts = await cursor.to_list(length=limit)

    if format == "csv":
        import csv
        import io
        output = io.StringIO()
        if posts:
            keys = list(posts[0].keys())
            writer = csv.DictWriter(output, fieldnames=keys)
            writer.writeheader()
            for post in posts:
                writer.writerow({k: str(v) for k, v in post.items()})
        return {"format": "csv", "data": output.getvalue(), "count": len(posts)}

    return {"format": "json", "data": posts, "count": len(posts)}


@router.get("/report")
async def export_report(platform: Optional[str] = Query(None)):
    import io

    clusters = await get_topic_clusters(platform=platform)
    cursor = await raw_posts_collection.find({})
    posts = await cursor.to_list(length=500)

    total = len(posts)
    fake_count = sum(1 for p in posts if p.get("label") == "fake")
    real_count = sum(1 for p in posts if p.get("label") == "real")
    platforms = {}
    authority_dist = {"official": 0, "journalist": 0, "organization": 0, "public": 0}
    sentiment_dist = {"positive": 0, "neutral": 0, "negative": 0}

    for p in posts:
        pf = p.get("platform", "unknown")
        platforms[pf] = platforms.get(pf, 0) + 1
        src_type = get_source_type(p.get("author", ""), pf)
        if src_type in authority_dist:
            authority_dist[src_type] += 1
        s = p.get("sentiment", {})
        if isinstance(s, dict):
            lbl = s.get("label", "neutral")
            if lbl in sentiment_dist:
                sentiment_dist[lbl] += 1

    lines = []
    lines.append("=" * 60)
    lines.append("  SocialPulse AI - Analysis Report")
    lines.append("=" * 60)
    lines.append(f"  Generated: {__import__('datetime').datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"  Platform filter: {platform or 'All'}")
    lines.append("")
    lines.append("OVERVIEW")
    lines.append("-" * 40)
    lines.append(f"  Total posts analyzed: {total}")
    lines.append(f"  Fake/Uncertain:       {fake_count} ({fake_count/total*100:.1f}%)" if total else "  No posts")
    lines.append(f"  Real/Verified:        {real_count} ({real_count/total*100:.1f}%)" if total else "  No posts")
    lines.append(f"  Platforms:            {', '.join(f'{k} ({v})' for k, v in platforms.items())}")
    lines.append("")
    lines.append("AUTHORITY DISTRIBUTION")
    lines.append("-" * 40)
    for k, v in authority_dist.items():
        lines.append(f"  {k:>12}: {v} ({v/total*100:.1f}%)" if total else f"  {k:>12}: 0")
    lines.append("")
    lines.append("SENTIMENT DISTRIBUTION")
    lines.append("-" * 40)
    for k, v in sentiment_dist.items():
        lines.append(f"  {k:>12}: {v} ({v/total*100:.1f}%)" if total else f"  {k:>12}: 0")
    lines.append("")
    lines.append("TOPIC CLUSTERS")
    lines.append("-" * 40)
    for c in clusters[:10]:
        lines.append(f"  {c['topic']}: {c['post_count']} posts, authority={c['avg_authority_score']:.1f}, engagement={c['avg_engagement']:.1f}")
    lines.append("")
    lines.append("=" * 60)
    lines.append("  End of Report")
    lines.append("=" * 60)

    output = io.BytesIO()
    content = "\n".join(lines)
    output.write(content.encode("utf-8"))
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=socialpulse-report.txt"},
    )
