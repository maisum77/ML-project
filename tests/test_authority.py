from backend.app.models.authority_sources import (
    is_authoritative_handle,
    is_authoritative_domain,
    get_source_type,
    get_authority_score,
)


class TestAuthoritativeHandles:
    def test_who_is_official(self):
        assert is_authoritative_handle("who", "twitter") is True

    def test_nasa_is_official(self):
        assert is_authoritative_handle("nasa", "twitter") is True

    def test_random_person_not_official(self):
        assert is_authoritative_handle("randomuser123", "twitter") is False

    def test_case_insensitive(self):
        assert is_authoritative_handle("WHO", "twitter") is True
        assert is_authoritative_handle("Nasa", "twitter") is True

    def test_reddit_official(self):
        assert is_authoritative_handle("nasa", "reddit") is True

    def test_empty_handle(self):
        assert is_authoritative_handle("", "twitter") is False
        assert is_authoritative_handle(None, "twitter") is False


class TestAuthoritativeDomains:
    def test_who_domain(self):
        assert is_authoritative_domain("https://who.int/health-info") is True

    def test_nasa_domain(self):
        assert is_authoritative_domain("https://nasa.gov/mission") is True

    def test_random_domain(self):
        assert is_authoritative_domain("https://random-blog.com/article") is False

    def test_empty_url(self):
        assert is_authoritative_domain("") is False
        assert is_authoritative_domain(None) is False


class TestSourceType:
    def test_official_handle(self):
        assert get_source_type("who", "twitter") == "official"

    def test_journalist_handle(self):
        assert get_source_type("breakingnews247", "twitter") == "journalist"

    def test_public_handle(self):
        assert get_source_type("randomuser", "twitter") == "public"

    def test_org_domain(self):
        assert get_source_type("somesite", "twitter", url="https://who.int/article") == "org"


class TestAuthorityScore:
    def test_official_score(self):
        score = get_authority_score("who", "twitter", verified=True)
        assert score >= 90

    def test_public_score(self):
        score = get_authority_score("randomuser", "twitter", verified=False)
        assert score <= 50

    def test_verified_bonus(self):
        unverified = get_authority_score("somehandle", "twitter", verified=False)
        verified = get_authority_score("somehandle", "twitter", verified=True)
        assert verified > unverified