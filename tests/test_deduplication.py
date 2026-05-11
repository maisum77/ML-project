import pytest
from data_collection.deduplication import Deduplicator


def test_get_text_hash():
    dedup = Deduplicator()
    hash1 = dedup.get_text_hash("Hello World")
    hash2 = dedup.get_text_hash("hello world")
    assert hash1 == hash2


def test_filter_duplicates():
    dedup = Deduplicator()
    posts = [
        {"id": "1", "title": "Breaking News", "text": "Something happened"},
        {"id": "2", "title": "Breaking News", "text": "Something happened"},
        {"id": "3", "title": "Different News", "text": "Another thing"},
    ]
    unique = dedup.filter_duplicates(posts)
    assert len(unique) == 2


def test_clear_cache():
    dedup = Deduplicator()
    dedup.filter_duplicates([{"id": "1", "title": "Test", "text": "test"}])
    dedup.clear_cache()
    assert len(dedup.seen_hashes) == 0
