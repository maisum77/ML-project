"""
Geolocation service: extract locations from posts and build geo-distribution data
for the globe visualization.
"""

import re
from typing import Optional, List, Dict
from data.location_mappings import get_location_for_subreddit, get_location_for_url

try:
    import spacy
    _nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    _nlp = spacy.load("en_core_web_sm")

KNOWN_CITIES = {
    "geneva": (46.2044, 6.1432),
    "zurich": (47.3769, 8.5417),
    "berlin": (52.5200, 13.4050),
    "london": (51.5074, -0.1278),
    "paris": (48.8566, 2.3522),
    "madrid": (40.4168, -3.7038),
    "rome": (41.9028, 12.4964),
    "moscow": (55.7558, 37.6173),
    "istanbul": (41.0082, 28.9784),
    "dubai": (25.2048, 55.2708),
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090),
    "beijing": (39.9042, 116.4074),
    "shanghai": (31.2304, 121.4737),
    "tokyo": (35.6762, 139.6503),
    "seoul": (37.5665, 126.9780),
    "singapore": (1.3521, 103.8198),
    "sydney": (-33.8688, 151.2093),
    "new york": (40.7128, -74.0060),
    "washington": (38.9072, -77.0369),
    "san francisco": (37.7749, -122.4194),
    "los angeles": (34.0522, -118.2437),
    "chicago": (41.8781, -87.6298),
    "toronto": (43.6532, -79.3832),
    "mexico city": (19.4326, -99.1332),
    "sao paulo": (-23.5505, -46.6333),
    "buenos aires": (-34.6037, -58.3816),
    "cairo": (30.0444, 31.2357),
    "lagos": (6.5244, 3.3792),
    "nairobi": (-1.2921, 36.8219),
    "johannesburg": (-26.2041, 28.0473),
    "kyiv": (50.4501, 30.5234),
    "warsaw": (52.2297, 21.0122),
    "amsterdam": (52.3676, 4.9041),
    "brussels": (50.8503, 4.3517),
    "stockholm": (59.3293, 18.0686),
    "oslo": (59.9139, 10.7522),
    "copenhagen": (55.6761, 12.5683),
    "helsinki": (60.1699, 24.9384),
    "athens": (37.9838, 23.7275),
    "jakarta": (-6.2088, 106.8456),
    "bangkok": (13.7563, 100.5018),
    "manila": (14.5995, 120.9842),
    "kuala lumpur": (3.1390, 101.6869),
}

KNOWN_COUNTRIES = {
    "usa": (37.0902, -95.7129), "united states": (37.0902, -95.7129),
    "uk": (55.3781, -3.4360), "united kingdom": (55.3781, -3.4360),
    "canada": (56.1304, -106.3468),
    "australia": (-25.2744, 133.7751),
    "india": (20.5937, 78.9629),
    "china": (35.8617, 104.1954),
    "japan": (36.2048, 138.2529),
    "germany": (51.1657, 10.4515),
    "france": (46.6034, 1.8883),
    "brazil": (-14.2350, -51.9253),
    "russia": (61.5240, 105.3188),
    "south africa": (-30.5595, 22.9375),
    "nigeria": (9.0820, 8.6753),
    "kenya": (-0.0236, 37.9062),
    "egypt": (26.8206, 30.8025),
    "pakistan": (30.3753, 69.3451),
    "bangladesh": (23.6850, 90.3563),
    "indonesia": (-0.7893, 113.9213),
    "mexico": (23.6345, -102.5528),
    "argentina": (-38.4161, -63.6167),
    "spain": (40.4637, -3.7492),
    "italy": (41.8719, 12.5674),
    "turkey": (38.9637, 35.2433),
    "iran": (32.4279, 53.6880),
    "saudi arabia": (23.8859, 45.0792),
    "uae": (23.4241, 53.8478),
    "south korea": (35.9078, 127.7669),
    "vietnam": (14.0583, 108.2772),
    "thailand": (15.8700, 100.9925),
    "philippines": (12.8797, 121.7740),
    "netherlands": (52.1326, 5.2913),
    "belgium": (50.5039, 4.4699),
    "sweden": (60.1282, 18.6435),
    "poland": (51.9194, 19.1451),
    "ukraine": (48.3794, 31.1656),
    "portugal": (39.3999, -8.2245),
    "greece": (39.0742, 21.8243),
    "israel": (31.0461, 34.8516),
    "ireland": (53.1424, -7.6921),
    "new zealand": (-40.9006, 174.8860),
    "singapore": (1.3521, 103.8198),
    "malaysia": (4.2105, 101.9758),
    "colombia": (4.5709, -74.2973),
    "chile": (-35.6751, -71.5430),
    "peru": (-9.1900, -75.0152),
}


def extract_locations_from_text(text: str) -> List[Dict]:
    if not text:
        return []
    doc = _nlp(text[:1000])
    locations = []
    for ent in doc.ents:
        if ent.label_ in ("GPE", "LOC"):
            name = ent.text.strip()
            lower = name.lower()
            if lower in KNOWN_CITIES:
                lat, lng = KNOWN_CITIES[lower]
                locations.append({"name": name, "lat": lat, "lng": lng, "source": "ner"})
            elif lower in KNOWN_COUNTRIES:
                lat, lng = KNOWN_COUNTRIES[lower]
                locations.append({"name": name, "lat": lat, "lng": lng, "source": "ner"})
    return locations


def extract_location_for_post(post: dict) -> Optional[Dict]:
    if not post:
        return None

    subreddit = post.get("subreddit")
    sub_loc = get_location_for_subreddit(subreddit)
    if sub_loc:
        return {"name": sub_loc["city"], "lat": sub_loc["lat"], "lng": sub_loc["lng"], "source": "subreddit"}

    url = post.get("url")
    url_loc = get_location_for_url(url)
    if url_loc:
        return {"name": url_loc["city"], "lat": url_loc["lat"], "lng": url_loc["lng"], "source": "url"}

    author_loc = post.get("author_location")
    if author_loc:
        lower = author_loc.lower().strip()
        for city, coords in KNOWN_CITIES.items():
            if city in lower:
                return {"name": author_loc, "lat": coords[0], "lng": coords[1], "source": "profile"}
        for country, coords in KNOWN_COUNTRIES.items():
            if country in lower:
                return {"name": author_loc, "lat": coords[0], "lng": coords[1], "source": "profile"}
        return None

    text = (post.get("title") or "") + " " + (post.get("text") or "")
    locations = extract_locations_from_text(text)
    if locations:
        return locations[0]

    return None


async def get_geo_distribution(topic: Optional[str] = None, platform: Optional[str] = None) -> List[Dict]:
    from backend.app.core.database import raw_posts_collection
    cursor = await raw_posts_collection.find({})
    posts = await cursor.to_list(length=500)

    if platform:
        posts = [p for p in posts if p.get("platform") == platform]

    if topic:
        topic_lower = topic.lower()
        posts = [
            p for p in posts
            if topic_lower in ((p.get("title") or "") + " " + (p.get("text") or "")).lower()
            or topic_lower in " ".join(p.get("hashtags", [])).lower()
        ]

    points = {}
    for post in posts:
        lat = post.get("location_lat")
        lng = post.get("location_lng")
        if lat is not None and lng is not None:
            key = f"{round(lat, 1)}_{round(lng, 1)}"
        else:
            location = extract_location_for_post(post)
            if not location:
                continue
            lat, lng = location["lat"], location["lng"]
            key = f"{round(lat, 1)}_{round(lng, 1)}"

        if key not in points:
            points[key] = {
                "lat": lat,
                "lng": lng,
                "count": 0,
                "posts": [],
            }
        points[key]["count"] += 1
        points[key]["posts"].append({
            "id": post.get("id"),
            "author": post.get("author"),
            "title": (post.get("title") or post.get("text", ""))[:100],
            "sentiment": post.get("sentiment", {}).get("label"),
            "platform": post.get("platform"),
        })

    result = sorted(points.values(), key=lambda x: x["count"], reverse=True)
    return result


async def get_globe_data() -> Dict:
    from backend.app.core.database import raw_posts_collection

    cursor = await raw_posts_collection.find({})
    posts = await cursor.to_list(length=500)

    arcs = []
    points = {}

    posts_with_locations = []
    for post in posts:
        lat = post.get("location_lat")
        lng = post.get("location_lng")
        if lat is None or lng is None:
            location = extract_location_for_post(post)
            if location:
                lat, lng = location["lat"], location["lng"]
            else:
                continue

        posts_with_locations.append(post)
        key = f"{round(lat, 1)}_{round(lng, 1)}"
        if key not in points:
            points[key] = {"lat": lat, "lng": lng, "size": 0, "sentiment": {"positive": 0, "neutral": 0, "negative": 0}}
        points[key]["size"] += 1
        sentiment = post.get("sentiment", {}).get("label", "neutral")
        points[key]["sentiment"][sentiment] += 1

    sorted_posts = sorted(posts_with_locations, key=lambda x: x.get("created_at", ""), reverse=True)
    for i, post in enumerate(sorted_posts):
        parent_id = post.get("parent_id")
        if parent_id:
            origin = post.get("origin_post_id")
            if origin:
                origin_post = None
                origin_lat = origin_lng = None
                for op in posts:
                    if op.get("id") == origin:
                        origin_post = op
                        break
                if origin_post:
                    origin_lat = origin_post.get("location_lat")
                    origin_lng = origin_post.get("location_lng")
                    if origin_lat is None:
                        loc = extract_location_for_post(origin_post)
                        if loc:
                            origin_lat, origin_lng = loc["lat"], loc["lng"]

                current_lat = post.get("location_lat")
                current_lng = post.get("location_lng")

                if origin_lat and origin_lng and current_lat and current_lng:
                    arcs.append({
                        "startLat": origin_lat,
                        "startLng": origin_lng,
                        "endLat": current_lat,
                        "endLng": current_lng,
                    })

    return {
        "points": list(points.values()),
        "arcs": arcs,
    }


async def get_topic_globe_data(topic: str) -> Dict:
    from backend.app.core.database import raw_posts_collection

    cursor = await raw_posts_collection.find({})
    posts = await cursor.to_list(length=500)

    topic_lower = topic.lower()
    posts = [
        p for p in posts
        if topic_lower in ((p.get("title") or "") + " " + (p.get("text") or "")).lower()
        or topic_lower in " ".join(p.get("hashtags", [])).lower()
        or topic_lower in (p.get("subreddit") or "").lower()
    ]

    arcs = []
    points = {}

    posts_with_locations = []
    for post in posts:
        lat = post.get("location_lat")
        lng = post.get("location_lng")
        if lat is None or lng is None:
            location = extract_location_for_post(post)
            if location:
                lat, lng = location["lat"], location["lng"]
            else:
                continue

        posts_with_locations.append(post)
        key = f"{round(lat, 1)}_{round(lng, 1)}"
        if key not in points:
            points[key] = {"lat": lat, "lng": lng, "size": 0, "sentiment": {"positive": 0, "neutral": 0, "negative": 0}, "name": ""}
        points[key]["size"] += 1
        sentiment = post.get("sentiment", {}).get("label", "neutral")
        points[key]["sentiment"][sentiment] += 1
        loc_name = None
        if post.get("location_lat") and post.get("location_lng"):
            loc = extract_location_for_post(post)
            if loc:
                loc_name = loc.get("name")
        else:
            location = extract_location_for_post(post)
            if location:
                loc_name = location.get("name")
        if loc_name and not points[key]["name"]:
            points[key]["name"] = loc_name

    sorted_posts = sorted(posts_with_locations, key=lambda x: x.get("created_at", ""), reverse=True)
    for post in sorted_posts:
        parent_id = post.get("parent_id")
        if parent_id:
            origin = post.get("origin_post_id")
            if origin:
                origin_post = None
                origin_lat = origin_lng = None
                for op in posts:
                    if op.get("id") == origin:
                        origin_post = op
                        break
                if origin_post:
                    origin_lat = origin_post.get("location_lat")
                    origin_lng = origin_post.get("location_lng")
                    if origin_lat is None:
                        loc = extract_location_for_post(origin_post)
                        if loc:
                            origin_lat, origin_lng = loc["lat"], loc["lng"]

                current_lat = post.get("location_lat")
                current_lng = post.get("location_lng")

                if origin_lat and origin_lng and current_lat and current_lng:
                    arcs.append({
                        "startLat": origin_lat,
                        "startLng": origin_lng,
                        "endLat": current_lat,
                        "endLng": current_lng,
                    })

    return {
        "topic": topic,
        "points": list(points.values()),
        "arcs": arcs,
        "total_posts": len(posts_with_locations),
    }
