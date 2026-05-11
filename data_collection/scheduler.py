import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from data_collection.reddit_collector import RedditCollector
from data_collection.twitter_collector import TwitterCollector
from data_collection.deduplication import Deduplicator
from data_processing.preprocessor import TextPreprocessor
from backend.app.core.database import raw_posts_collection

scheduler = AsyncIOScheduler()
deduplicator = Deduplicator()
preprocessor = TextPreprocessor()


async def collect_reddit_data():
    print("[Scheduler] Fetching Reddit data...")
    collector = RedditCollector()
    posts = collector.fetch_all_subreddits(limit=25)
    unique_posts = deduplicator.filter_duplicates(posts)
    saved = await collector.save_posts(unique_posts)
    print(f"[Scheduler] Saved {saved} new Reddit posts")


async def collect_twitter_data():
    print("[Scheduler] Fetching Twitter data...")
    collector = TwitterCollector()
    tweets = collector.fetch_all_trending(max_results=50)
    unique_tweets = deduplicator.filter_duplicates(tweets)
    saved = await collector.save_tweets(unique_tweets)
    print(f"[Scheduler] Saved {saved} new Twitter posts")


async def process_new_posts():
    print("[Scheduler] Processing new posts...")
    pipeline = [
        {"$match": {"processed": {"$ne": True}}},
        {"$limit": 100}
    ]
    posts = await raw_posts_collection.aggregate(pipeline).to_list(length=100)

    for post in posts:
        text = post.get("title", "") + " " + post.get("text", "")
        cleaned = preprocessor.clean_text(text)
        lang = preprocessor.detect_language(text)
        tokens = preprocessor.tokenize(cleaned)

        await raw_posts_collection.update_one(
            {"id": post["id"]},
            {"$set": {
                "cleaned_text": cleaned,
                "language": lang,
                "tokens": tokens,
                "processed": True,
            }}
        )

    print(f"[Scheduler] Processed {len(posts)} posts")


def start_scheduler():
    scheduler.add_job(
        collect_reddit_data,
        trigger=IntervalTrigger(minutes=15),
        id="reddit_collector",
        replace_existing=True,
    )
    scheduler.add_job(
        collect_twitter_data,
        trigger=IntervalTrigger(minutes=15),
        id="twitter_collector",
        replace_existing=True,
    )
    scheduler.add_job(
        process_new_posts,
        trigger=IntervalTrigger(minutes=5),
        id="post_processor",
        replace_existing=True,
    )
    scheduler.start()
    print("[Scheduler] Started data collection jobs (15-min intervals)")


def stop_scheduler():
    scheduler.shutdown()
