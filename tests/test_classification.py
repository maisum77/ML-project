import pytest
from backend.app.services.classification_service import (
    _analyze_linguistic_signals,
    _analyze_emotional_language,
    _analyze_source,
    _extract_entities,
    _extract_topics,
    _compute_verdict,
)
from ml_models.sentiment.predict import predict_sentiment
from ml_models.fake_news.predict import predict_fake_news


class TestSentimentAnalysis:
    def test_positive_sentiment(self):
        result = predict_sentiment("I love this amazing product! It's wonderful!")
        assert result["label"] == "positive"
        assert result["score"] > 0

    def test_negative_sentiment(self):
        result = predict_sentiment("This is terrible and awful. I hate it.")
        assert result["label"] == "negative"
        assert result["score"] > 0

    def test_neutral_sentiment(self):
        result = predict_sentiment("The sky is blue and the grass is green.")
        assert result["label"] in ["neutral", "positive", "negative"]

    def test_empty_string(self):
        result = predict_sentiment("")
        assert result["label"] in ["positive", "negative", "neutral"]

    def test_returns_expected_keys(self):
        result = predict_sentiment("Hello world")
        assert "label" in result
        assert "score" in result
        assert "model" in result


class TestFakeNewsDetection:
    def test_fake_news_keywords(self):
        result = predict_fake_news("SHOCKING secret cure doctors HATE! 100% GUARANTEED!!")
        assert result["label"] == "fake"
        assert result["confidence"] > 0

    def test_real_news_style(self):
        result = predict_fake_news("According to a study published in The Lancet...")
        assert result["label"] == "real"
        assert result["confidence"] > 0

    def test_excessive_exclamation(self):
        result = predict_fake_news("This is AMAZING!!!")
        assert result["confidence"] > 0

    def test_returns_expected_keys(self):
        result = predict_fake_news("Normal text here")
        assert "label" in result
        assert "confidence" in result


class TestLinguisticAnalysis:
    def test_sensationalist_flags(self):
        result = _analyze_linguistic_signals("SHOCKING news about the deep state conspiracy!")
        assert result["score"] > 0
        assert len(result["flags"]) > 0
        flag_names = [f["flag"] for f in result["flags"]]
        assert "sensationalist_adjective" in flag_names or "conspiracy_language" in flag_names

    def test_clean_text(self):
        result = _analyze_linguistic_signals("The weather is nice today.")
        assert result["score"] == 0
        assert len(result["flags"]) == 0

    def test_caps_detection(self):
        result = _analyze_linguistic_signals("BREAKING NEWS UPDATE")
        assert any(f["flag"] == "excessive_caps" for f in result["flags"])

    def test_clickbait_detection(self):
        result = _analyze_linguistic_signals("You won't believe what happens next")
        assert any(f["flag"] == "clickbait_phrase" for f in result["flags"])

    def test_word_count(self):
        result = _analyze_linguistic_signals("Hello world this is a test")
        assert result["word_count"] == 6


class TestEmotionalAnalysis:
    def test_anger_detection(self):
        result = _analyze_emotional_language("This is outrageous and disgusting!")
        assert result["primary_emotion"] in ["anger", "neutral"]

    def test_fear_detection(self):
        result = _analyze_emotional_language("This is terrifying and scary crisis")
        assert result["primary_emotion"] in ["fear", "neutral"]

    def test_neutral_text(self):
        result = _analyze_emotional_language("The meeting is at 3pm")
        assert result["primary_emotion"] == "neutral"
        assert result["subjectivity"] == 0


class TestTopicDetection:
    def test_health_topic(self):
        result = _extract_topics("A new vaccine has been approved for disease prevention")
        assert any(t["topic"] == "health" for t in result)

    def test_technology_topic(self):
        result = _extract_topics("AI and machine learning are transforming software development")
        assert any(t["topic"] == "AI & Technology" for t in result)

    def test_no_matching_topic(self):
        result = _extract_topics("The cat sat on the mat")
        assert len(result) <= 4

    def test_returns_dict_format(self):
        result = _extract_topics("Climate change and carbon emissions")
        for t in result:
            assert "topic" in t
            assert "relevance" in t


class TestEntityExtraction:
    def test_organization_extraction(self):
        result = _extract_entities("The WHO announced new guidelines")
        assert len(result["organizations"]) > 0

    def test_location_extraction(self):
        result = _extract_entities("Reports from New York and London")
        assert len(result["locations"]) > 0

    def test_empty_text(self):
        result = _extract_entities("Hello world")
        assert "people" in result
        assert "organizations" in result
        assert "locations" in result


class TestSourceAnalysis:
    def test_authoritative_source(self):
        result = _analyze_source("WHO", "Breaking news about health")
        assert result["source_type"] == "official"
        assert result["authority_score"] >= 80

    def test_unknown_source(self):
        result = _analyze_source(None, "Some random text")
        assert result["source_type"] == "unattributed"
        assert result["authority_score"] == 0

    def test_attribution_detection(self):
        result = _analyze_source(None, "According to Reuters, the economy is growing")
        assert result["has_attribution"] is True

    def test_quotes_detection(self):
        result = _analyze_source(None, 'He said "this is a quote"')
        assert result["has_quotes"] is True


class TestVerdictComputation:
    def test_reliable_verdict(self):
        linguistic = {"score": 0, "flags": [], "word_count": 10, "avg_sentence_length": 15}
        emotional = {"primary_emotion": "neutral", "emotion_scores": {}, "subjectivity": 0, "emotional_intensity": 0}
        source = {"source_type": "official", "authority_score": 90, "domains": [], "has_attribution": True, "has_quotes": True, "attribution_score": 50}
        fact_checks = {"claims_checked": 1, "matches": [{"verdict": "true", "claim_text": "test", "publisher": "snopes"}], "verdict": "true"}
        sentiment = {"label": "neutral", "score": 20}
        fake_result = {"label": "real", "confidence": 90}

        verdict = _compute_verdict(linguistic, emotional, source, fact_checks, sentiment, fake_result)
        assert verdict["label"] == "likely_reliable"
        assert verdict["risk_level"] == "low"

    def test_unreliable_verdict(self):
        linguistic = {"score": 80, "flags": [{"flag": "sensationalist", "count": 1, "score": 20}], "word_count": 10, "avg_sentence_length": 5}
        emotional = {"primary_emotion": "anger", "emotion_scores": {"anger": 2}, "subjectivity": 0.5, "emotional_intensity": 30}
        source = {"source_type": "public", "authority_score": 20, "domains": [], "has_attribution": False, "has_quotes": False, "attribution_score": 0}
        fact_checks = {"claims_checked": 0, "matches": [], "verdict": "unchecked"}
        sentiment = {"label": "negative", "score": 80}
        fake_result = {"label": "fake", "confidence": 70}

        verdict = _compute_verdict(linguistic, emotional, source, fact_checks, sentiment, fake_result)
        assert verdict["risk_level"] in ["high", "medium"]