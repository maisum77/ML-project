"""
Propagation service: traces the origin of a claim, builds the
cascade tree of who shared from whom, and ties in geo + authority.
"""

import hashlib
from typing import Optional, List, Dict
from backend.app.core.database import raw_posts_collection, propagation_collection
from backend.app.services.authority_service import check_post_authority
from backend.app.services.geo_service import extract_location_for_post


async def build_topic_hash(text: str) -> str:
    words = text.lower().split()
    significant = [w for w in words if len(w) > 3][:5]
    return hashlib.md5(" ".join(significant).encode()).hexdigest()[:16]


async def trace_origin(post_id: str) -> Optional[Dict]:
    post = await raw_posts_collection.find_one({"id": post_id})
    if not post:
        return None

    chain = [post]
    current = post
    visited = {post_id}
    max_depth = 20

    while current.get("parent_id") and len(chain) < max_depth:
        parent_id = current["parent_id"]
        if parent_id in visited:
            break
        visited.add(parent_id)
        parent = await raw_posts_collection.find_one({"id": parent_id})
        if parent:
            chain.insert(0, parent)
            current = parent
        else:
            break

    origin = chain[0]
    origin_authority = await check_post_authority(origin)

    cascade = []
    for i, p in enumerate(chain):
        authority = await check_post_authority(p)
        location = extract_location_for_post(p)

        cascade.append({
            "depth": i,
            "post_id": p.get("id"),
            "author": p.get("author"),
            "platform": p.get("platform"),
            "text": (p.get("title") or p.get("text", ""))[:150],
            "url": p.get("url"),
            "created_at": p.get("created_at"),
            "retweets": p.get("retweets", 0),
            "upvotes": p.get("upvotes", 0),
            "authority_score": authority["authority_score"],
            "author_type": authority["author_type"],
            "is_authentic": authority["is_authentic"],
            "location": location,
        })

    topic_text = (origin.get("title") or "") + " " + (origin.get("text") or "")
    topic_hash = await build_topic_hash(topic_text)

    await propagation_collection.insert_one({
        "id": f"trace_{post_id}_{int(p.get('created_at', '').replace('-', '').replace('T', '').replace(':', '')[:12] if p.get('created_at') else '0')}"[:64],
        "topic_hash": topic_hash,
        "origin_id": origin.get("id"),
        "origin_author": origin.get("author"),
        "origin_platform": origin.get("platform"),
        "origin_authority_score": origin_authority["authority_score"],
        "origin_is_authentic": origin_authority["is_authentic"],
        "chain_length": len(chain),
        "cascade": cascade,
    })

    return {
        "origin": {
            "post_id": origin.get("id"),
            "author": origin.get("author"),
            "platform": origin.get("platform"),
            "text": (origin.get("title") or origin.get("text", ""))[:200],
            "url": origin.get("url"),
            "created_at": origin.get("created_at"),
            "authority_score": origin_authority["authority_score"],
            "author_type": origin_authority["author_type"],
            "is_authentic": origin_authority["is_authentic"],
            "reasons": origin_authority["reasons"],
        },
        "chain_length": len(chain),
        "cascade": cascade,
    }


async def get_propagation_for_topic(topic: str) -> Dict:
    cursor = await raw_posts_collection.find({})
    posts = await cursor.to_list(length=500)

    topic_lower = topic.lower()
    topic_posts = [
        p for p in posts
        if topic_lower in ((p.get("title") or "") + " " + (p.get("text") or "")).lower()
        or any(topic_lower in h.lower() for h in p.get("hashtags", []))
    ]
    topic_posts.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    origins = {}
    cascades = {}
    for p in topic_posts:
        origin_id = p.get("origin_post_id")
        if origin_id:
            if origin_id not in cascades:
                cascades[origin_id] = {
                    "origin_id": origin_id,
                    "origin_author": None,
                    "nodes": [],
                }
            authority = await check_post_authority(p)
            location = extract_location_for_post(p)
            cascades[origin_id]["nodes"].append({
                "post_id": p.get("id"),
                "author": p.get("author"),
                "depth": p.get("propagation_depth", 0),
                "authority_score": authority["authority_score"],
                "author_type": authority["author_type"],
                "location": location,
                "retweets": p.get("retweets", 0),
                "upvotes": p.get("upvotes", 0),
            })
        else:
            authority = await check_post_authority(p)
            location = extract_location_for_post(p)
            origins[p.get("id")] = {
                "post_id": p.get("id"),
                "author": p.get("author"),
                "platform": p.get("platform"),
                "text": (p.get("title") or p.get("text", ""))[:150],
                "authority_score": authority["authority_score"],
                "author_type": authority["author_type"],
                "is_authentic": authority["is_authentic"],
                "location": location,
            }

    for origin_id, cascade in cascades.items():
        if origin_id in origins:
            cascade["origin_author"] = origins[origin_id]["author"]
            cascade["origin_authority_score"] = origins[origin_id]["authority_score"]
            cascade["origin_is_authentic"] = origins[origin_id]["is_authentic"]
        cascade["nodes"].sort(key=lambda x: x["depth"])

    geo_dist = []
    for p in topic_posts:
        loc = extract_location_for_post(p)
        if loc:
            geo_dist.append({
                "lat": loc["lat"],
                "lng": loc["lng"],
                "name": loc["name"],
                "post_id": p.get("id"),
                "author": p.get("author"),
            })

    return {
        "topic": topic,
        "total_posts": len(topic_posts),
        "origins": list(origins.values()),
        "cascades": list(cascades.values()),
        "geo_distribution": geo_dist,
    }
