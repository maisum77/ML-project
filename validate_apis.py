#!/usr/bin/env python3
"""Validate all APIs configured in .env"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test(label, func):
    try:
        print(f"\n  Testing {label}...", end=" ")
        result = func()
        print(result)
        return True if "OK" in str(result) else None
    except Exception as e:
        print(f"FAIL: {e}")
        return False

# ── 1. AWS DynamoDB ──────────────────────────────────────────
def validate_aws():
    import boto3
    key_id = os.getenv("AWS_ACCESS_KEY_ID", "")
    secret = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    region = os.getenv("AWS_REGION", "us-east-1")

    if not key_id or key_id.startswith("your_"):
        return "SKIP - no credentials configured"

    client = boto3.client(
        "dynamodb",
        region_name=region,
        aws_access_key_id=key_id,
        aws_secret_access_key=secret,
    )
    tables = client.list_tables(Limit=1)
    return f"OK - connected, tables found: {tables.get('TableNames', [])}"


# ── 2. Reddit API ────────────────────────────────────────────
def validate_reddit():
    import praw
    cid = os.getenv("REDDIT_CLIENT_ID", "")
    secret = os.getenv("REDDIT_CLIENT_SECRET", "")
    ua = os.getenv("REDDIT_USER_AGENT", "SocialPulseAI/1.0")

    if not cid or cid.startswith("your_"):
        return "SKIP - no credentials configured"

    reddit = praw.Reddit(client_id=cid, client_secret=secret, user_agent=ua)
    # Try to read-only fetch to verify auth
    me = reddit.user.me()
    if me:
        return f"OK - authenticated as u/{me.name}"
    # Script apps don't have a user, try reading a subreddit
    sub = reddit.subreddit("news")
    _ = sub.display_name  # this forces a request
    return "OK - authenticated (script app, read-only access confirmed)"


# ── 3. X / Twitter API ───────────────────────────────────────
def validate_twitter():
    import tweepy
    from urllib.parse import unquote

    bearer_raw = os.getenv("X_BEARER_TOKEN", "")
    bearer = unquote(bearer_raw)
    api_key = os.getenv("X_API_KEY", "")
    api_secret = os.getenv("X_API_SECRET", "")
    access_token = os.getenv("X_ACCESS_TOKEN", "")
    access_secret = os.getenv("X_ACCESS_TOKEN_SECRET", "")

    is_placeholder = lambda v: not v or v.startswith("your_")
    has_bearer = bearer_raw and not bearer_raw.startswith("your_")
    have_oauth1 = not any(is_placeholder(v) for v in [api_key, api_secret, access_token, access_secret])

    if not has_bearer and not have_oauth1:
        return "SKIP - no credentials configured"

    results = []

    # Strategy 1: Bearer token (app-only v2 API)
    if has_bearer:
        try:
            client = tweepy.Client(bearer_token=bearer, wait_on_rate_limit=True)
            resp = client.search_recent_tweets(query="test", max_results=5)
            results.append(f"bearer: OK ({len(resp.data or [])} tweets)")
        except Exception as e:
            err = str(e)
            if "402" in err:
                results.append(f"bearer: SKIP (402 - paid tier required)")
            else:
                results.append(f"bearer: FAIL - {err[:80]}")

    # Strategy 2: OAuth 1.0a User Context
    if have_oauth1:
        try:
            client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_secret,
                wait_on_rate_limit=True,
            )
            me = client.get_me()
            username = me.data.username if me.data else "read-only"
            results.append(f"OAuth1: OK - @{username}")
        except Exception as e:
            results.append(f"OAuth1: FAIL - {str(e)[:100]}")

    if results:
        return " | ".join(results)
    return "FAIL - no auth strategy worked"


# ── 4. Google Fact Check API ─────────────────────────────────
def validate_google_factcheck():
    import httpx
    key = os.getenv("GOOGLE_FACT_CHECK_API_KEY", "")

    if not key or key.startswith("your_"):
        return "SKIP - no credentials configured"

    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {"query": "covid vaccine", "key": key, "languageCode": "en"}

    with httpx.Client(timeout=15) as client:
        resp = client.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            claims = data.get("claims", [])
            return f"OK - {len(claims)} claims returned"
        elif resp.status_code == 403:
            return "FAIL - 403 Forbidden (API may not be enabled in Google Cloud Console)"
        else:
            return f"FAIL - HTTP {resp.status_code}: {resp.text[:150]}"


# ── 5. ClaimBuster API ───────────────────────────────────────
def validate_claimbuster():
    import httpx
    key = os.getenv("CLAIMBUSTER_API_KEY", "")

    if not key or key.startswith("your_"):
        return "SKIP - no credentials configured"

    url = "https://api.idaholab.ai/claimbuster/v1/score"
    params = {"text": "The earth is flat", "key": key}

    with httpx.Client(timeout=15) as client:
        resp = client.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            score = data.get("score", 0)
            return f"OK - score: {score}"
        elif resp.status_code == 403:
            return "FAIL - 403 Forbidden"
        else:
            return f"FAIL - HTTP {resp.status_code}: {resp.text[:150]}"


# ── Main ─────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("SocialPulse API Validation")
    print("=" * 55)

    results = {}
    results["AWS DynamoDB"] = test("AWS DynamoDB", validate_aws)
    results["Reddit"] = test("Reddit", validate_reddit)
    results["X/Twitter"] = test("X/Twitter", validate_twitter)
    results["Google Fact Check"] = test("Google Fact Check", validate_google_factcheck)
    results["ClaimBuster"] = test("ClaimBuster", validate_claimbuster)

    print("\n" + "=" * 55)
    print("SUMMARY")
    print("=" * 55)
    for name, passed in results.items():
        icon = "PASS" if passed is True else ("SKIP" if passed is None else "FAIL")
        print(f"  {icon}  {name}")
