from typing import Optional
from data_processing.preprocessor import TextPreprocessor
from backend.app.core.database import raw_posts_collection, cleaned_posts_collection

preprocessor = TextPreprocessor()


async def process_single_post(post_id: str):
    post = await raw_posts_collection.find_one({"id": post_id})
    if not post:
        return None

    text = (post.get("title", "") + " " + post.get("text", "")).strip()
    result = preprocessor.preprocess(text)

    cleaned_doc = {
        "id": post_id,
        "original_id": post_id,
        "source": post.get("source"),
        "platform": post.get("platform"),
        "original_text": text,
        "cleaned_text": result["cleaned"],
        "language": result["language"],
        "tokens": result["tokens"],
        "sentiment": result["sentiment"],
    }

    await cleaned_posts_collection.update_one(
        {"original_id": post_id},
        {"$set": cleaned_doc},
        upsert=True,
    )

    await raw_posts_collection.update_one(
        {"id": post_id},
        {"$set": {"processed": True, "sentiment": result["sentiment"]}},
    )

    return cleaned_doc


async def process_batch(limit: int = 100):
    cursor = raw_posts_collection.aggregate([
        {"$match": {"processed": {"$ne": True}}},
    ])
    posts = await cursor.to_list(length=limit)

    results = []
    for post in posts:
        result = await process_single_post(post["id"])
        if result:
            results.append(result)

    return results
