import praw
import hashlib
from datetime import datetime
from typing import Optional
from backend.app.core.config import get_settings
from backend.app.core.database import raw_posts_collection

settings = get_settings()


class RedditCollector:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
        )
        self.subreddits = [
            "news", "worldnews", "technology", "science", "politics",
            "programming", "machinelearning", "datascience",
        ]

    def fetch_hot_posts(self, subreddit_name: str, limit: int = 25) -> list:
        posts = []
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            for submission in subreddit.hot(limit=limit):
                post = {
                    "id": f"reddit_{submission.id}",
                    "source": "reddit",
                    "platform": "reddit",
                    "title": submission.title,
                    "text": submission.selftext or "",
                    "author": str(submission.author),
                    "upvotes": submission.score,
                    "comments_count": submission.num_comments,
                    "retweets": 0,
                    "likes": 0,
                    "url": f"https://reddit.com{submission.permalink}",
                    "subreddit": subreddit_name,
                    "hashtags": self._extract_hashtags(submission.title),
                    "created_at": datetime.utcfromtimestamp(submission.created_utc),
                    "fetched_at": datetime.utcnow(),
                }
                posts.append(post)
        except Exception as e:
            print(f"Error fetching from r/{subreddit_name}: {e}")
        return posts

    def fetch_all_subreddits(self, limit: int = 25) -> list:
        all_posts = []
        for sub in self.subreddits:
            posts = self.fetch_hot_posts(sub, limit)
            all_posts.extend(posts)
        return all_posts

    async def save_posts(self, posts: list) -> int:
        saved = 0
        for post in posts:
            post_id = post["id"]
            existing = await raw_posts_collection.find_one({"id": post_id})
            if not existing:
                await raw_posts_collection.insert_one(post)
                saved += 1
        return saved

    def _extract_hashtags(self, text: str) -> list:
        import re
        return re.findall(r'#\w+', text)

    def get_post_hash(self, text: str) -> str:
        return hashlib.md5(text.lower().strip().encode()).hexdigest()
