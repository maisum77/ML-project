from backend.app.core.dynamodb import raw_posts, cleaned_posts, trends, sentiment, fact_checks, propagation

raw_posts_collection = raw_posts
cleaned_posts_collection = cleaned_posts
trends_collection = trends
sentiment_collection = sentiment
fact_checks_collection = fact_checks
propagation_collection = propagation


async def init_db():
    print("[Database] Using AWS DynamoDB")


async def get_db():
    return True


async def seed_demo_data():
    from datetime import datetime, timezone

    existing = await raw_posts_collection.count_documents({})
    if existing > 0:
        return

    now = datetime.now(timezone.utc).isoformat()
    demo_posts = [
        {
            "id": "twitter_demo_origin",
            "source": "twitter",
            "platform": "twitter",
            "title": None,
            "text": "Breaking: New study shows social media affects mental health significantly. More research needed.",
            "author": "WHO",
            "upvotes": 0,
            "comments_count": 89,
            "retweets": 456,
            "likes": 1203,
            "url": "https://twitter.com/i/status/demo_origin",
            "subreddit": None,
            "hashtags": ["#MentalHealth", "#Research"],
            "created_at": now,
            "fetched_at": now,
            "processed": "true",
            "sentiment": {"label": "neutral", "score": 0.1},
            "parent_id": None,
            "origin_post_id": "twitter_demo_origin",
            "propagation_depth": 0,
            "author_verified": True,
            "author_type": "official",
            "authority_score": 95,
            "author_location": "Geneva, Switzerland",
            "location_lat": 46.2044,
            "location_lng": 6.1432,
        },
        {
            "id": "twitter_demo_retweet1",
            "source": "twitter",
            "platform": "twitter",
            "title": None,
            "text": "RT @WHO: Breaking: New study shows social media affects mental health significantly.",
            "author": "NYTimes",
            "upvotes": 0,
            "comments_count": 34,
            "retweets": 234,
            "likes": 890,
            "url": "https://twitter.com/i/status/demo_rt1",
            "subreddit": None,
            "hashtags": ["#MentalHealth"],
            "created_at": now,
            "fetched_at": now,
            "processed": "true",
            "sentiment": {"label": "neutral", "score": 0.05},
            "parent_id": "twitter_demo_origin",
            "origin_post_id": "twitter_demo_origin",
            "propagation_depth": 1,
            "author_verified": True,
            "author_type": "journalist",
            "authority_score": 80,
            "author_location": "New York, USA",
            "location_lat": 40.7128,
            "location_lng": -74.006,
        },
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
            "processed": "true",
            "sentiment": {"label": "positive", "score": 0.85},
            "parent_id": None,
            "origin_post_id": "reddit_demo_1",
            "propagation_depth": 0,
            "author_verified": False,
            "author_type": "public",
            "authority_score": 30,
            "author_location": None,
            "location_lat": None,
            "location_lng": None,
        },
        {
            "id": "twitter_demo_retweet2",
            "source": "twitter",
            "platform": "twitter",
            "title": None,
            "text": "RT @NYTimes: Mental health study shows alarming trends in social media usage.",
            "author": "health_reporter",
            "upvotes": 0,
            "comments_count": 12,
            "retweets": 45,
            "likes": 234,
            "url": "https://twitter.com/i/status/demo_rt2",
            "subreddit": None,
            "hashtags": ["#MentalHealth"],
            "created_at": now,
            "fetched_at": now,
            "processed": "true",
            "sentiment": {"label": "negative", "score": -0.3},
            "parent_id": "twitter_demo_retweet1",
            "origin_post_id": "twitter_demo_origin",
            "propagation_depth": 2,
            "author_verified": False,
            "author_type": "public",
            "authority_score": 30,
            "author_location": "London, UK",
            "location_lat": 51.5074,
            "location_lng": -0.1278,
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
            "processed": "true",
            "sentiment": {"label": "negative", "score": -0.6},
            "parent_id": None,
            "origin_post_id": "reddit_demo_2",
            "propagation_depth": 0,
            "author_verified": False,
            "author_type": "public",
            "authority_score": 30,
            "author_location": None,
            "location_lat": None,
            "location_lng": None,
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
            "processed": "true",
            "sentiment": {"label": "positive", "score": 0.92},
            "parent_id": None,
            "origin_post_id": "twitter_demo_2",
            "propagation_depth": 0,
            "author_verified": False,
            "author_type": "public",
            "authority_score": 30,
            "author_location": "Berlin, Germany",
            "location_lat": 52.52,
            "location_lng": 13.405,
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
            "processed": "true",
            "sentiment": {"label": "negative", "score": -0.75},
            "parent_id": None,
            "origin_post_id": "reddit_demo_3",
            "propagation_depth": 0,
            "author_verified": False,
            "author_type": "public",
            "authority_score": 30,
            "author_location": None,
            "location_lat": None,
            "location_lng": None,
        },
    ]

    demo_propagation = [
        {"id": "prop_mental_health_0", "topic_hash": "mental_health_study", "post_id": "twitter_demo_origin", "depth": 0, "author": "WHO", "author_type": "official", "authority_score": 95},
        {"id": "prop_mental_health_1", "topic_hash": "mental_health_study", "post_id": "twitter_demo_retweet1", "depth": 1, "author": "NYTimes", "author_type": "journalist", "authority_score": 80},
        {"id": "prop_mental_health_2", "topic_hash": "mental_health_study", "post_id": "twitter_demo_retweet2", "depth": 2, "author": "health_reporter", "author_type": "public", "authority_score": 30},
    ]

    demo_trends = [
        {"topic_id": "AI & Technology", "count": 1523, "avg_engagement": 892.5, "platform": "reddit"},
        {"topic_id": "Climate Change", "count": 987, "avg_engagement": 654.2, "platform": "reddit"},
        {"topic_id": "Mental Health", "count": 756, "avg_engagement": 432.1, "platform": "twitter"},
        {"topic_id": "Renewable Energy", "count": 543, "avg_engagement": 321.8, "platform": "twitter"},
        {"topic_id": "Space Exploration", "count": 432, "avg_engagement": 289.4, "platform": "reddit"},
    ]

    demo_sentiment = [
        {"id": "sentiment_positive", "label": "positive", "count": 2},
        {"id": "sentiment_neutral", "label": "neutral", "count": 1},
        {"id": "sentiment_negative", "label": "negative", "count": 2},
    ]

    for post in demo_posts:
        await raw_posts_collection.insert_one(post)
    for trend in demo_trends:
        await trends_collection.insert_one(trend)
    for s in demo_sentiment:
        await sentiment_collection.insert_one(s)
    for p in demo_propagation:
        await propagation_collection.insert_one(p)

    print(f"[Database] Seeded demo data into DynamoDB ({len(demo_posts)} posts, {len(demo_trends)} trends, {len(demo_propagation)} propagation chains)")
