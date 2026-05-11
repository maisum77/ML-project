from fastapi import APIRouter, Query
from typing import Optional
from backend.app.core.database import raw_posts_collection

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

    cursor = raw_posts_collection.find(query).limit(limit)
    posts = await cursor.to_list(length=limit)

    if format == "csv":
        import csv
        import io
        output = io.StringIO()
        if posts:
            writer = csv.DictWriter(output, fieldnames=posts[0].keys())
            writer.writeheader()
            for post in posts:
                writer.writerow({k: str(v) for k, v in post.items()})
        return {"format": "csv", "data": output.getvalue(), "count": len(posts)}

    return {"format": "json", "data": posts, "count": len(posts)}
