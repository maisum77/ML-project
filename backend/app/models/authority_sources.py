"""
Known authority sources for credibility scoring.
These are manually curated lists of official accounts, government agencies,
major news organizations, and verified experts.
"""

# Twitter/X handles of official sources (lowercase)
OFFICIAL_TWITTER = {
    # World Health Organizations
    "who", "whowpro", "who_europe", "whoemro", "whoafro",
    "pahowho", "whophilippines", "whosrilanka", "whoindonesia",
    "whomalaysia", "whothailand", "whovietnam",

    # United Nations
    "un", "un_spokesperson", "unocha", "unicef", "unhcr",
    "wfp", "undp", "unep", "unwomens", "unpeacekeeping",

    # US Government
    "potus", "vp", "whitehouse", "statedept", "deptofdefense",
    "thejusticedept", "ustreasury", "dhsgov", "fema", "fbi",
    "secgov", "nasa", "nih", "cdcgov", "fdagov", "usda",
    "energygov", "noaa", "nsagov",

    # US State Governors (selected)
    "govkathyhochul", "govgavinnewsom", "govgregabbott",
    "govrondesantis", "govedinslee", "govjbprtizker",

    # UK Government
    "10downingstreet", "foreignoffice", "ukhomeoffice",
    "ministryofdefence", "hmtreasury", "dhscgovuk",
    "defencehq",

    # EU
    "eu_commission", "eucouncil", "europarl_en", "ecb",
    "eu_eeas", "nato",

    # Other Governments
    "gcainfo", "dfat", "mfat_nz", "indiandiplomacy",
    "pmoindia", "meaindia", "narendramodi",

    # Major News Organizations
    "bbcworld", "bbcbreaking", "cnn", "cnnbrk", "reuters",
    "ap", "nytimes", "washingtonpost", "wsj", "bloomberg",
    "guardian", "guardiannews", "telegraph", "independent",
    "skynews", "skynewsbreak", "channel4news", "itvnews",
    "abc", "abcnews", "nbcnews", "cbsnews", "foxnews",
    "msnbc", "pbsnewshour", "npr",

    # Fact Checking Organizations
    "politifact", "snopes", "factcheckdotorg",
    "fullfact", "afpfactcheck",

    # Tech / Science
    "nasa", "nasa_technology", "spacex", "cern",
    "mit", "nature", "sciencemagazine",

    # Health
    "cdcgov", "cdc_ehealth", "nhsengland", "publichealthon",
    "jhu", "mayoclinic", "lancet",
}

# Reddit usernames of official sources
OFFICIAL_REDDIT = {
    "who", "unitednations", "nasa", "cdcgov", "whitehouse",
}

# Known official subreddits (posts in these are from orgs)
OFFICIAL_SUBREDDITS = {
    "announcements", "blog",
}

# Organization domains that indicate authority
AUTHORITY_DOMAINS = {
    "who.int", "un.org", "nasa.gov", "cdc.gov", "nih.gov",
    "fda.gov", "state.gov", "whitehouse.gov", "gov.uk",
    "europa.eu", "nato.int", "reuters.com", "apnews.com",
    "bbc.com", "bbc.co.uk", "nature.com", "science.org",
    "lancet.com", "mayoclinic.org", "jhu.edu", "mit.edu",
    "harvard.edu", "stanford.edu", "ox.ac.uk", "cam.ac.uk",
}


def is_authoritative_handle(handle: str, platform: str = "twitter") -> bool:
    if not handle:
        return False
    handle_lower = handle.lower().lstrip("@").lstrip("u/")
    if platform == "twitter":
        return handle_lower in OFFICIAL_TWITTER
    elif platform == "reddit":
        return handle_lower in OFFICIAL_REDDIT
    return False


def is_authoritative_subreddit(subreddit: str) -> bool:
    if not subreddit:
        return False
    return subreddit.lower() in OFFICIAL_SUBREDDITS


def is_authoritative_domain(url: str) -> bool:
    if not url:
        return False
    for domain in AUTHORITY_DOMAINS:
        if domain in url:
            return True
    return False


def get_source_type(handle: str, platform: str, subreddit: str = None, url: str = None) -> str:
    if is_authoritative_handle(handle, platform):
        return "official"
    if is_authoritative_subreddit(subreddit):
        return "official"
    if is_authoritative_domain(url):
        return "org"

    handle_lower = (handle or "").lower()
    if any(w in handle_lower for w in ["news", "press", "media", "times", "post", "daily", "chronicle", "gazette", "herald", "journal", "tribune", "dispatch"]):
        return "journalist"

    return "public"


def get_authority_score(handle: str, platform: str, verified: bool = False,
                        subreddit: str = None, url: str = None) -> float:
    score = 0

    source_type = get_source_type(handle, platform, subreddit, url)
    if source_type == "official":
        score = 95
    elif source_type == "org":
        score = 85
    elif source_type == "journalist":
        score = 65
    else:
        score = 30

    if verified:
        score = min(score + 15, 100)

    if is_authoritative_domain(url):
        score = min(score + 10, 100)

    return score
