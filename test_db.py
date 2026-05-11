import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
from backend.app.core.database import init_db, seed_demo_data, raw_posts_collection

async def test():
    await init_db()
    await seed_demo_data()
    posts = await raw_posts_collection.find({}).sort("upvotes", -1).limit(10)
    result = await posts.to_list(length=10)
    print(f"Found {len(result)} posts")
    for p in result[:2]:
        title = p.get("title") or p.get("text", "")[:50]
        print(f"  - {title}")

asyncio.run(test())
