import tweepy
import hashlib
from datetime import datetime
from typing import Optional
from backend.app.core.config import get_settings
from backend.app.core.database import raw_posts_collection
from backend.app.models.authority_sources import is_authoritative_handle, get_authority_score, get_source_type

settings = get_settings()


class TwitterCollector:
    def __init__(self):
        self.client = tweepy.Client(
            bearer_token=settings.x_bearer_token,
            consumer_key=settings.x_api_key,
            consumer_secret=settings.x_api_secret,
            access_token=settings.x_access_token,
            access_token_secret=settings.x_access_token_secret,
        )
        self.trending_queries = [
            "AI news", "breaking news", "technology", "science",
            "machine learning", "climate change", "politics",
        ]

    def fetch_trending_tweets(self, query: str, max_results: int = 50) -> list:
        tweets = []
        try:
            response = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=["created_at", "public_metrics", "author_id", "entities", "referenced_tweets", "in_reply_to_user_id"],
                expansions=["author_id", "referenced_tweets.id"],
                user_fields=["verified", "verified_type", "location", "username"],
            )
            if not response.data:
                return tweets

            users = {}
            if response.includes and "users" in response.includes:
                users = {u.id: u for u in response.includes["users"]}

            for tweet in response.data:
                metrics = tweet.public_metrics or {}
                hashtags = []
                if tweet.entities and "hashtags" in tweet.entities:
                    hashtags = [h["tag"] for h in tweet.entities["hashtags"]]

                parent_id = None
                referenced = tweet.referenced_tweets
                if referenced:
                    for ref in referenced:
                        if ref.type in ("retweeted", "quoted", "replied_to"):
                            parent_id = f"twitter_{ref.id}"
                            break

                user = users.get(tweet.author_id) if tweet.author_id else None
                author_username = user.username if user else str(tweet.author_id)
                author_verified = getattr(user, "verified", False) if user else False
                author_location = user.location if user and user.location else None
                author_type = get_source_type(author_username, "twitter")
                authority_score = get_authority_score(author_username, "twitter", author_verified)

                tweet_data = {
                    "id": f"twitter_{tweet.id}",
                    "source": "twitter",
                    "platform": "twitter",
                    "title": None,
                    "text": tweet.text,
                    "author": author_username,
                    "upvotes": 0,
                    "comments_count": metrics.get("reply_count", 0),
                    "retweets": metrics.get("retweet_count", 0),
                    "likes": metrics.get("like_count", 0),
                    "url": f"https://twitter.com/i/status/{tweet.id}",
                    "subreddit": None,
                    "hashtags": hashtags,
                    "created_at": tweet.created_at or datetime.utcnow(),
                    "fetched_at": datetime.utcnow(),
                    "parent_id": parent_id,
                    "origin_post_id": None,
                    "propagation_depth": 0,
                    "author_verified": author_verified,
                    "author_type": author_type,
                    "authority_score": authority_score,
                    "author_location": author_location,
                    "location_lat": None,
                    "location_lng": None,
                }
                tweets.append(tweet_data)
        except Exception as e:
            print(f"Error fetching tweets for '{query}': {e}")
        return tweets

    def fetch_all_trending(self, max_results: int = 50) -> list:
        all_tweets = []
        for query in self.trending_queries:
            tweets = self.fetch_trending_tweets(query, max_results)
            all_tweets.extend(tweets)
        return all_tweets

    async def save_tweets(self, tweets: list) -> int:
        saved = 0
        for tweet in tweets:
            tweet_id = tweet["id"]
            existing = await raw_posts_collection.find_one({"id": tweet_id})
            if not existing:
                if tweet.get("parent_id"):
                    parent = await raw_posts_collection.find_one({"id": tweet["parent_id"]})
                    if parent:
                        tweet["origin_post_id"] = parent.get("origin_post_id") or parent.get("id")
                        tweet["propagation_depth"] = (parent.get("propagation_depth") or 0) + 1
                    else:
                        tweet["origin_post_id"] = tweet_id
                else:
                    tweet["origin_post_id"] = tweet_id

                await raw_posts_collection.insert_one(tweet)
                saved += 1
        return saved

    def get_post_hash(self, text: str) -> str:
        return hashlib.md5(text.lower().strip().encode()).hexdigest()
