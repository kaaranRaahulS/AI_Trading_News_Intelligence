# deduplication.py
import re
from dataclasses import dataclass


def normalize_title(title: str) -> str:
    if not title:
        return ""
    
    normalized = title.lower()
    normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized.strip()


@dataclass
class DeduplicationResult:
    unique_articles: list
    duplicates_removed: int
    total_input: int
    
    def summary(self) -> str:
        return (
            f"{self.total_input} articles → "
            f"{len(self.unique_articles)} unique "
            f"({self.duplicates_removed} duplicates removed)"
        )


def deduplicate_articles(articles: list, key: str = "title") -> DeduplicationResult:
    
    seen: set[str] = set()
    unique: list = []
    duplicates = 0
    
    for article in articles:
        if hasattr(article, key):
            title = getattr(article, key)
        else:
            title = article.get(key, "")
        
        normalized = normalize_title(title)
        
        if normalized in seen:
            duplicates += 1
            continue
        
        seen.add(normalized)
        unique.append(article)
    
    return DeduplicationResult(
        unique_articles=unique,
        duplicates_removed=duplicates,
        total_input=len(articles),
    )