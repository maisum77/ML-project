from backend.app.services.clustering_service import (
    TOPIC_KEYWORDS,
    _compute_similarity,
    _extract_post_keywords,
)


class TestTopicKeywords:
    def test_all_topics_have_keywords(self):
        for topic, keywords in TOPIC_KEYWORDS.items():
            assert len(keywords) > 0, f"Topic {topic} has no keywords"

    def test_topic_names_are_strings(self):
        for topic in TOPIC_KEYWORDS:
            assert isinstance(topic, str)


class TestComputeSimilarity:
    def test_identical_sets(self):
        a = {"ai", "ml", "data"}
        b = {"ai", "ml", "data"}
        assert _compute_similarity(a, b) == 1.0

    def test_disjoint_sets(self):
        a = {"ai", "ml"}
        b = {"health", "vaccine"}
        assert _compute_similarity(a, b) == 0.0

    def test_partial_overlap(self):
        a = {"ai", "ml", "data"}
        b = {"ai", "health", "data"}
        sim = _compute_similarity(a, b)
        assert 0 < sim < 1

    def test_empty_sets(self):
        assert _compute_similarity(set(), set()) == 0.0
        assert _compute_similarity({"ai"}, set()) == 0.0


class TestExtractPostKeywords:
    def test_health_post(self):
        post = {
            "title": "New vaccine approved",
            "text": "The WHO has approved a new vaccine for disease prevention",
            "hashtags": ["#health", "#vaccine"],
            "subreddit": None,
        }
        topics = _extract_post_keywords(post)
        assert isinstance(topics, set)
        assert any("Health" in t for t in topics)

    def test_tech_post(self):
        post = {
            "title": "AI breakthrough in machine learning",
            "text": "New algorithm for deep learning applications",
            "hashtags": ["#AI", "#technology"],
            "subreddit": None,
        }
        topics = _extract_post_keywords(post)
        assert isinstance(topics, set)
        assert any("AI & Technology" in t for t in topics)

    def test_empty_post(self):
        post = {"title": "", "text": "Hello world", "hashtags": [], "subreddit": None}
        topics = _extract_post_keywords(post)
        assert isinstance(topics, set)

    def test_subreddit_detection(self):
        post = {
            "title": "Cool new tech",
            "text": "Testing",
            "hashtags": [],
            "subreddit": "technology",
        }
        topics = _extract_post_keywords(post)
        assert any("AI & Technology" in t for t in topics)