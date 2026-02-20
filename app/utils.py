import logging
import os
from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from urllib.parse import urlencode, quote
import feedparser
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

#Optional dependency 
try:
    from newspaper import Article as NewspaperArticle
    HAS_NEWSPAPER = True
except ImportError:
    HAS_NEWSPAPER = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv()

MARKETAUX_API_KEY: str = os.getenv("MARKETAUX_API_KEY", "")
MARKETAUX_BASE_URL: str = "https://api.marketaux.com/v1/news/all"
GOOGLE_NEWS_RSS_URL: str = "https://news.google.com/rss/search"

DEFAULT_TIMEOUT: int = 10
MIN_CONTENT_LENGTH: int = 50 


@dataclass
class NewsArticle:
    title: str
    link: str
    published: str
    content: str = ""
    source: str = ""

    def display(self, index: int) -> None:
        separator = "-" * 60
        print(f"\n{index}. {self.title}")
        print(f"   Published : {self.published}")
        print(f"   Link      : {self.link}")
        if self.content:
            preview = self.content[:300].replace("\n", " ")
            print(f"   Preview   : {preview}…")
        print(separator)

#Fetching full article content from the url provided in the RSS feed. This is optional and can be toggled when fetching news from Google News.
def fetch_article_content(url: str) -> str:
    if not url:
        return ""

    #newspaper3k
    if HAS_NEWSPAPER:
        try:
            article = NewspaperArticle(url, language="en")
            article.download()
            article.parse()
            text = article.text.strip()
            if len(text) >= MIN_CONTENT_LENGTH and "JavaScript" not in text:
                return text
        except Exception as exc:
            logger.debug("newspaper3k failed for %s: %s", url, exc)

    #BeautifulSoup
    try:
        response = requests.get(url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text(strip=True) for p in paragraphs)
        if len(text) >= MIN_CONTENT_LENGTH:
            return text
    except Exception as exc:
        logger.debug("BeautifulSoup scrape failed for %s: %s", url, exc)

    logger.warning("Could not retrieve content from: %s", url)
    return ""


#Marketaux API
def fetch_news_marketaux(
    search_query: str = (
        '(("gold" | xau | bullion) | '
        '("inflation" | "cpi" | "interest rates" | "federal reserve" | '
        '"treasury yields" | dollar | dxy)) -crypto -bitcoin'
    ),
    language: str = "en",
    limit: int = 3,
    published_on: Optional[date] = None,
) -> list[NewsArticle]:

    if not MARKETAUX_API_KEY:
        raise EnvironmentError(
            "MARKETAUX_API_KEY is not set. Add it to your .env file."
        )

    params: dict = {
        "search": search_query,
        "language": language,
        "filter_entities": "true",
        "limit": limit,
        "api_token": MARKETAUX_API_KEY,
    }
    if published_on:
        params["published_on"] = published_on.isoformat()

    try:
        response = requests.get(
            MARKETAUX_BASE_URL, params=params, timeout=DEFAULT_TIMEOUT
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        logger.error("Marketaux HTTP error: %s", exc)
        return []
    except requests.exceptions.RequestException as exc:
        logger.error("Marketaux request failed: %s", exc)
        return []

    try:
        payload = response.json()
    except ValueError as exc:
        logger.error("Failed to parse Marketaux JSON: %s", exc)
        return []

    articles: list[NewsArticle] = []
    for item in payload.get("data", []):
        articles.append(
            NewsArticle(
                title=item.get("title", ""),
                link=item.get("url", ""),
                published=item.get("published_at", ""),
                content=item.get("description", ""),
                source="marketaux",
            )
        )

    logger.info("Marketaux: fetched %d article(s).", len(articles))
    return articles

def fetch_news_google(
    query: str,
    num_articles: int = 10,
    fetch_full_content: bool = True,
) -> list[NewsArticle]:

    rss_url = f"{GOOGLE_NEWS_RSS_URL}?q={quote(query)}"

    try:
        response = requests.get(rss_url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        logger.error("Google News RSS request failed: %s", exc)
        return []

    feed = feedparser.parse(response.content)
    articles: list[NewsArticle] = []

    for entry in feed.entries[:num_articles]:
        link: str = entry.get("link", "")

        source_url: str = ""
        if hasattr(entry, "source") and entry.source:
            source_url = entry.source.get("href", "")

        content = ""
        if fetch_full_content:
            content = fetch_article_content(source_url or link)

        articles.append(
            NewsArticle(
                title=entry.get("title", ""),
                link=link,
                published=entry.get("published", ""),
                content=content,
                source="google_news",
            )
        )

    logger.info("Google News: fetched %d article(s) for query '%s'.", len(articles), query)
    return articles


if __name__ == "__main__":

    #Marketaux API
    marketaux_articles = fetch_news_marketaux(
        limit=3,
        published_on=date(2026, 2, 18),
    )
    print(f"\n{'='*60}")
    print(f"  Marketaux – {len(marketaux_articles)} article(s)")
    print(f"{'='*60}")
    for i, article in enumerate(marketaux_articles, start=1):
        article.display(i)

    #Google News
    google_articles = fetch_news_google("Finance Gold", num_articles=2)
    print(f"\n{'='*60}")
    print(f"  Google News – {len(google_articles)} article(s)")
    print(f"{'='*60}")
    for i, article in enumerate(google_articles, start=1):
        article.display(i)