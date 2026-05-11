import hashlib
from difflib import SequenceMatcher


class Deduplicator:
    def __init__(self, similarity_threshold: float = 0.85):
        self.seen_hashes: set = set()
        self.seen_texts: list = []
        self.similarity_threshold = similarity_threshold

    def get_text_hash(self, text: str) -> str:
        normalized = text.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()

    def is_similar(self, text1: str, text2: str) -> bool:
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio() > self.similarity_threshold

    def filter_duplicates(self, posts: list) -> list:
        unique_posts = []
        for post in posts:
            text = post.get("title", "") + " " + post.get("text", "")
            text_hash = self.get_text_hash(text)

            if text_hash in self.seen_hashes:
                continue

            is_dup = False
            if len(text) > 50:
                for seen_text in self.seen_texts:
                    if self.is_similar(text, seen_text):
                        is_dup = True
                        break

            if not is_dup:
                self.seen_hashes.add(text_hash)
                self.seen_texts.append(text)
                unique_posts.append(post)

        return unique_posts

    def clear_cache(self):
        self.seen_hashes.clear()
        self.seen_texts.clear()
