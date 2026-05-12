#!/usr/bin/env python3
"""
SocialPulse AI - Demo Script
Populates fresh demo data and exercises all API endpoints for live presentation.

Usage:
    python scripts/demo.py [--api-url http://localhost:8000]
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone

try:
    import httpx
except ImportError:
    print("Installing httpx...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx"])
    import httpx


API_URL = "http://localhost:8000/api/v1"

SAMPLE_TEXTS = [
    {
        "text": "SHOCKING: Doctors HATE this one weird trick to cure cancer! 100% GUARANTEED!! The deep state doesn't want you to know!",
        "source": "@fakehealth",
        "expected": "likely_unreliable or needs_verification",
    },
    {
        "text": "According to a peer-reviewed study published in The Lancet, regular cardiovascular exercise reduces the risk of heart disease by approximately 30 percent, confirming decades of epidemiological research.",
        "source": "@WHO",
        "expected": "likely_reliable",
    },
    {
        "text": "Breaking: New legislation proposed in Congress aims to address carbon emissions through a comprehensive pricing mechanism, building on existing EPA regulatory frameworks.",
        "source": "@reuters",
        "expected": "likely_reliable",
    },
    {
        "text": "URGENT: The government is HIDING the truth about 5G towers causing illness! Share before they delete this!!",
        "source": "@conspiracynews99",
        "expected": "likely_unreliable",
    },
    {
        "text": "NASA's Perseverance rover has successfully collected rock samples on Mars that show evidence of ancient water activity, according to mission scientists at JPL.",
        "source": "@nasa",
        "expected": "likely_reliable",
    },
]


def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_result(label: str, data: dict):
    print(f"\n  {label}:")
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"    {key}:")
                for k2, v2 in value.items():
                    print(f"      {k2}: {v2}")
            elif isinstance(value, list) and len(value) > 5:
                print(f"    {key}: [{len(value)} items]")
            else:
                print(f"    {key}: {value}")
    else:
        print(f"    {data}")


def main():
    parser = argparse.ArgumentParser(description="SocialPulse AI Demo")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API base URL")
    args = parser.parse_args()

    api_url = args.api_url.rstrip("/")
    client = httpx.Client(base_url=api_url, timeout=30)

    print_section("Health Check")
    try:
        r = client.get("/health")
        print(f"  Status: {r.json()}")
    except Exception as e:
        print(f"  ERROR: Cannot connect to {api_url}")
        print(f"  Make sure the backend is running: python3 -m uvicorn backend.app.main:app --port 8000")
        sys.exit(1)

    print_section("Authentication - Register & Login")
    try:
        r = client.post("/api/v1/auth/register", json={
            "username": "demo_user",
            "email": "demo@socialpulse.ai",
            "password": "demo123",
        })
        if r.status_code == 200:
            data = r.json()
            print(f"  Registered: {data['user']['username']}")
            token = data["token"]
        elif "already exists" in str(r.json()).lower() or r.status_code == 400:
            print("  User already exists, logging in...")
            r = client.post("/api/v1/auth/login", json={
                "username": "demo_user",
                "password": "demo123",
            })
            data = r.json()
            token = data["token"]
            print(f"  Logged in: {data['user']['username']}")
        else:
            print(f"  Registration failed: {r.status_code} {r.text}")
            token = None
    except Exception as e:
        print(f"  Auth failed: {e}")
        token = None

    if token:
        headers = {"Authorization": f"Bearer {token}"}
        r = client.get("/api/v1/auth/me", headers=headers)
        print_result("User Profile", r.json())

    print_section("Detailed Text Classification")
    for sample in SAMPLE_TEXTS[:3]:
        try:
            r = client.post("/api/v1/classify/detailed", json={
                "text": sample["text"],
                "source": sample.get("source"),
            })
            if r.status_code == 200:
                data = r.json()
                verdict = data["verdict"]
                print(f"\n  Text: {sample['text'][:80]}...")
                print(f"  Verdict: {verdict['label']} (risk: {verdict['risk_level']}, confidence: {verdict['confidence']}%)")
                print(f"  Explanation: {verdict['explanation']}")
                print(f"  Sentiment: {data['analysis']['sentiment']['label']} ({data['analysis']['sentiment']['score']}%)")
                flags = data['analysis']['linguistic_signals']['flags']
                if flags:
                    print(f"  Flags: {', '.join(f['flag'] for f in flags)}")
                topics = data['analysis']['topic_detection']
                if topics:
                    print(f"  Topics: {', '.join(t['topic'] for t in topics)}")
            else:
                print(f"  Classification failed: {r.status_code}")
        except Exception as e:
            print(f"  Error: {e}")

    print_section("Keyword Alerts")
    if token:
        for keyword in ["climate", "vaccine", "AI"]:
            try:
                r = client.post("/api/v1/auth/alerts", json={"keyword": keyword}, headers=headers)
                print(f"  Added alert: {keyword}")
            except Exception:
                pass

    print_section("Topic Clusters")
    try:
        r = client.get("/api/v1/trending/clusters")
        if r.status_code == 200:
            data = r.json()
            print(f"  Found {data['count']} clusters")
            for cluster in data.get("clusters", []):
                print(f"  - {cluster['topic']}: {cluster['post_count']} posts, avg authority: {cluster['avg_authority_score']}")
        else:
            print(f"  Clusters unavailable: {r.status_code}")
    except Exception as e:
        print(f"  Error: {e}")

    print_section("Authority Scorecard")
    try:
        r = client.get("/api/v1/authority/scorecard")
        if r.status_code == 200:
            data = r.json()
            print(f"  Total tracked sources: {data['total_sources']}")
            print(f"  Twitter sources: {data['twitter_sources']}")
            print(f"  Reddit sources: {data['reddit_sources']}")
            print(f"  Authority domains: {data['authority_domains']}")
            print(f"  Type distribution: {data['type_distribution']}")
        else:
            print(f"  Scorecard unavailable: {r.status_code}")
    except Exception as e:
        print(f"  Error: {e}")

    print_section("Authority Check")
    for handle in ["@WHO", "@nasa", "@randomuser123"]:
        try:
            r = client.get(f"/api/v1/authority/check?author={handle.lstrip('@')}&platform=twitter")
            if r.status_code == 200:
                data = r.json()
                print(f"  {handle}: type={data['author_type']}, score={data['authority_score']}, authentic={data['is_authentic']}")
        except Exception:
            pass

    print_section("Demo Complete!")
    print(f"\n  API Docs: {api_url}/docs")
    print(f"  Frontend: http://localhost:3000")
    print(f"  Health: {api_url}/health")

    client.close()


if __name__ == "__main__":
    main()