from typing import Optional
from backend.app.core.database import trends_collection, raw_posts_collection
from data_collection.reddit_collector import RedditCollector
from data_collection.twitter_collector import TwitterCollector
from data_collection.deduplication import Deduplicator
from data_processing.preprocessor import TextPreprocessor
from ml_models.sentiment.predict import predict_sentiment

deduplicator = Deduplicator()
preprocessor = TextPreprocessor()


async def _fetch_fresh_data(platform: Optional[str] = None):
    posts = []
    if platform in (None, "reddit"):
        try:
            collector = RedditCollector()
            reddit_posts = collector.fetch_all_subreddits(limit=10)
            posts.extend(reddit_posts)
        except Exception as e:
            print(f"[Trending] Reddit fetch error: {e}")

    if platform in (None, "twitter"):
        try:
            collector = TwitterCollector()
            twitter_posts = collector.fetch_all_trending(max_results=20)
            posts.extend(twitter_posts)
        except Exception as e:
            print(f"[Trending] Twitter fetch error: {e}")

    if not posts:
        cursor = (await raw_posts_collection.find({})).sort("upvotes", -1).limit(20)
        return await cursor.to_list(length=20)

    unique = deduplicator.filter_duplicates(posts)

    for post in unique:
        text = (post.get("title") or "") + " " + (post.get("text") or "")
        sentiment = predict_sentiment(text)
        post["sentiment"] = {"label": sentiment["label"], "score": sentiment["score"]}
        post["processed"] = True

        existing = await raw_posts_collection.find_one({"id": post["id"]})
        if not existing:
            await raw_posts_collection.insert_one(post)

    grouped = {}
    for post in unique:
        key = post.get("subreddit") or (post.get("hashtags", ["trending"])[0] if post.get("hashtags") else "trending")
        if key not in grouped:
            grouped[key] = {"_id": key, "count": 0, "avg_engagement": 0, "posts": [], "total_engagement": 0}
        grouped[key]["count"] += 1
        engagement = post.get("upvotes", 0) + post.get("comments_count", 0) + post.get("retweets", 0) + post.get("likes", 0)
        grouped[key]["total_engagement"] += engagement
        grouped[key]["posts"].append({
            "title": post.get("title"),
            "text": (post.get("text") or "")[:200],
            "url": post.get("url"),
            "sentiment": post.get("sentiment"),
        })

    for g in grouped.values():
        g["avg_engagement"] = g["total_engagement"] / g["count"] if g["count"] > 0 else 0
        del g["total_engagement"]

    return sorted(grouped.values(), key=lambda x: x["avg_engagement"], reverse=True)[:10]


async def get_trending_topics(platform: Optional[str] = None, limit: int = 10):
    topics = await _fetch_fresh_data(platform=platform)
    return topics[:limit]


async def get_trending_realtime(hours: int = 1):
    topics = await _fetch_fresh_data()
    return topics[:10]
