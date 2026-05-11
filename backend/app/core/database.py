from motor.motor_asyncio import AsyncIOMotorClient
from backend.app.core.config import get_settings
from datetime import datetime, timezone

settings = get_settings()

mongodb_available = False
client = None
db = None

_in_memory_data = {
    "raw_posts": [],
    "cleaned_posts": [],
    "trends": [],
    "fact_checks": [],
    "sentiment": [],
}


def _serialize_value(v):
    if isinstance(v, datetime):
        return v.isoformat()
    return v


def _serialize_doc(doc):
    return {k: _serialize_value(v) for k, v in doc.items()}


class InMemoryCursor:
    def __init__(self, data):
        self.data = [_serialize_doc(d) for d in data]
        self._sort_field = None
        self._sort_order = 1
        self._skip = 0
        self._limit = None

    def sort(self, field, order=1):
        self._sort_field = field
        self._sort_order = order
        return self

    def skip(self, count):
        self._skip = count
        return self

    def limit(self, count):
        self._limit = count
        return self

    async def to_list(self, length=None):
        result = list(self.data)
        if self._sort_field:
            result.sort(key=lambda x: x.get(self._sort_field, 0), reverse=(self._sort_order == -1))
        result = result[self._skip:]
        if self._limit:
            result = result[:self._limit]
        return result


class InMemoryCollection:
    def __init__(self, name):
        self.name = name

    def find(self, query=None, **kwargs):
        data = _in_memory_data.get(self.name, [])
        if query:
            filtered = []
            for item in data:
                match = True
                for k, v in query.items():
                    if item.get(k) != v:
                        match = False
                        break
                if match:
                    filtered.append(item)
            return InMemoryCursor(filtered)
        return InMemoryCursor(data)

    async def find_one(self, query=None):
        data = _in_memory_data.get(self.name, [])
        if not query:
            return _serialize_doc(data[0]) if data else None
        for item in data:
            match = True
            for k, v in query.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                return _serialize_doc(item)
        return None

    async def insert_one(self, doc):
        _in_memory_data[self.name].append(doc)
        return doc

    async def update_one(self, query, update, upsert=False):
        data = _in_memory_data.get(self.name, [])
        for item in data:
            match = True
            for k, v in query.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                set_data = update.get("$set", {})
                item.update(set_data)
                return type("obj", (object,), {"modified_count": 1})()
        if upsert:
            new_doc = dict(query)
            new_doc.update(update.get("$set", {}))
            _in_memory_data[self.name].append(new_doc)
        return type("obj", (object,), {"modified_count": 0})()

    async def count_documents(self, query=None):
        data = _in_memory_data.get(self.name, [])
        if not query:
            return len(data)
        count = 0
        for item in data:
            match = True
            for k, v in query.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                count += 1
        return count

    def aggregate(self, pipeline):
        data = _in_memory_data.get(self.name, [])
        return InMemoryCursor(data)


class CollectionProxy:
    def __init__(self, name):
        self.name = name
        self._collection = None

    def _get(self):
        if self._collection is None:
            if mongodb_available and db is not None:
                self._collection = db[self.name]
            else:
                self._collection = InMemoryCollection(self.name)
        return self._collection

    def find(self, query=None, **kwargs):
        return self._get().find(query, **kwargs)

    async def find_one(self, query=None):
        return await self._get().find_one(query)

    async def insert_one(self, doc):
        return await self._get().insert_one(doc)

    async def update_one(self, query, update, upsert=False):
        return await self._get().update_one(query, update, upsert)

    async def count_documents(self, query=None):
        return await self._get().count_documents(query)

    def aggregate(self, pipeline):
        return self._get().aggregate(pipeline)


raw_posts_collection = CollectionProxy("raw_posts")
cleaned_posts_collection = CollectionProxy("cleaned_posts")
trends_collection = CollectionProxy("trends")
fact_checks_collection = CollectionProxy("fact_checks")
sentiment_collection = CollectionProxy("sentiment")


async def init_db():
    global client, db, mongodb_available

    try:
        client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=3000)
        await client.admin.command("ping")
        db = client[settings.mongodb_db_name]
        mongodb_available = True
        print("[Database] Connected to MongoDB")
    except Exception as e:
        print(f"[Database] MongoDB not available, using in-memory storage")
        mongodb_available = False


async def get_db():
    return db


async def seed_demo_data():
    now = datetime.now(timezone.utc).isoformat()
    demo_posts = [
        {
            "id": "reddit_demo_1",
            "source": "reddit",
            "platform": "reddit",
            "title": "AI breakthrough in medical diagnosis announced",
            "text": "Researchers have developed a new AI system that can detect diseases with 99% accuracy.",
            "author": "tech_user",
            "upvotes": 1523,
            "comments_count": 342,
            "retweets": 0,
            "likes": 0,
            "url": "https://reddit.com/r/technology/demo1",
            "subreddit": "technology",
            "hashtags": ["#AI", "#Healthcare"],
            "created_at": now,
            "fetched_at": now,
            "sentiment": {"label": "positive", "score": 0.85},
        },
        {
            "id": "twitter_demo_1",
            "source": "twitter",
            "platform": "twitter",
            "title": None,
            "text": "Breaking: New study shows social media affects mental health significantly. More research needed.",
            "author": "news_bot",
            "upvotes": 0,
            "comments_count": 89,
            "retweets": 456,
            "likes": 1203,
            "url": "https://twitter.com/i/status/demo1",
            "subreddit": None,
            "hashtags": ["#MentalHealth", "#Research"],
            "created_at": now,
            "fetched_at": now,
            "sentiment": {"label": "neutral", "score": 0.1},
        },
        {
            "id": "reddit_demo_2",
            "source": "reddit",
            "platform": "reddit",
            "title": "Fake news spreads faster than real news, study confirms",
            "text": "A comprehensive study from MIT shows that false information spreads 6 times faster than truth on social platforms.",
            "author": "science_fan",
            "upvotes": 2891,
            "comments_count": 567,
            "retweets": 0,
            "likes": 0,
            "url": "https://reddit.com/r/science/demo2",
            "subreddit": "science",
            "hashtags": ["#FakeNews", "#Research"],
            "created_at": now,
            "fetched_at": now,
            "sentiment": {"label": "negative", "score": -0.6},
        },
        {
            "id": "twitter_demo_2",
            "source": "twitter",
            "platform": "twitter",
            "title": None,
            "text": "Exciting developments in renewable energy! Solar power costs hit record low worldwide.",
            "author": "green_tech",
            "upvotes": 0,
            "comments_count": 45,
            "retweets": 892,
            "likes": 3421,
            "url": "https://twitter.com/i/status/demo2",
            "subreddit": None,
            "hashtags": ["#Solar", "#CleanEnergy"],
            "created_at": now,
            "fetched_at": now,
            "sentiment": {"label": "positive", "score": 0.92},
        },
        {
            "id": "reddit_demo_3",
            "source": "reddit",
            "platform": "reddit",
            "title": "Climate change report shows alarming trends",
            "text": "The latest IPCC report indicates that global temperatures could rise by 2.7C by 2100 without immediate action.",
            "author": "climate_watch",
            "upvotes": 4521,
            "comments_count": 1203,
            "retweets": 0,
            "likes": 0,
            "url": "https://reddit.com/r/worldnews/demo3",
            "subreddit": "worldnews",
            "hashtags": ["#ClimateChange"],
            "created_at": now,
            "fetched_at": now,
            "sentiment": {"label": "negative", "score": -0.75},
        },
    ]

    demo_trends = [
        {"_id": "AI & Technology", "count": 1523, "avg_engagement": 892.5, "platform": "reddit"},
        {"_id": "Climate Change", "count": 987, "avg_engagement": 654.2, "platform": "reddit"},
        {"_id": "Mental Health", "count": 756, "avg_engagement": 432.1, "platform": "twitter"},
        {"_id": "Renewable Energy", "count": 543, "avg_engagement": 321.8, "platform": "twitter"},
        {"_id": "Space Exploration", "count": 432, "avg_engagement": 289.4, "platform": "reddit"},
    ]

    demo_sentiment = [
        {"_id": "positive", "count": 2},
        {"_id": "neutral", "count": 1},
        {"_id": "negative", "count": 2},
    ]

    if mongodb_available and db is not None:
        existing = await db["raw_posts"].count_documents({})
        if existing > 0:
            return
        for post in demo_posts:
            await db["raw_posts"].insert_one(post)
        for trend in demo_trends:
            await db["trends"].insert_one(trend)
        for s in demo_sentiment:
            await db["sentiment"].insert_one(s)
        print("[Database] Seeded demo data into MongoDB")
    else:
        if len(_in_memory_data["raw_posts"]) > 0:
            return
        for post in demo_posts:
            await raw_posts_collection.insert_one(post)
        for trend in demo_trends:
            await trends_collection.insert_one(trend)
        for s in demo_sentiment:
            await sentiment_collection.insert_one(s)
        print("[Database] Seeded demo data for in-memory storage")
