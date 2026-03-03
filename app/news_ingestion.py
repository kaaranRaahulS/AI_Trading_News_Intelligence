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

#logging setup 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
)
logger = logging.getLogger(__name__)

#Optional dependency 
try:
    from newspaper import Article as NewsArticle
    HAS_NEWSPAPER = True
except ImportError:
    HAS_NEWSPAPER = False

load_dotenv()
GNEWSIO_API_KEY: str = os.getenv("GNEWSIO_API_KEY", "")
MARKETAUX_API_KEY: str = os.getenv("MARKETAUX_API_KEY", "")

MARKETAUX_BASE_URL: str = "https://api.marketaux.com/v1/news/all"
GNEWSIO_BASE_URL: str = "https://gnews.io/api/v4/search"
GOOGLE_NEWS_RSS_URL: str = "https://news.google.com/rss/search"


DEFAULT_TIMEOUT: int = 10
MIN_CONTENT_LENGTH: int = 50 


@dataclass
class NewsArticle:
    title: str
    published: str
    source: str = ""
    link: str = ""
    content: str = ""

#GNews.io API
def fetch_news_gnewsio(
    query: str = ("gold price OR XAUUSD OR bullion",
        "gold inflation OR gold CPI",
        "gold federal reserve OR gold interest rates",
        "gold treasury yields OR gold dollar"),
    num_articles: int = 10,
    api_key: str = GNEWSIO_API_KEY,
    ) -> list[NewsArticle]:
    if not api_key:
        raise EnvironmentError(
            "GNEWSIO_API_KEY is not set. Add it to your .env file."
        )

    params: dict = {
        "q": query,
        "lang": "en",
        "max": num_articles,
        "token": api_key,
    }

    try:
        response = requests.get(
            GNEWSIO_BASE_URL, params=params, timeout=DEFAULT_TIMEOUT
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        logger.error("GNews.io HTTP error: %s", exc)
        return []
    except requests.exceptions.RequestException as exc:
        logger.error("GNews.io request failed: %s", exc)
        return []

    try:
        payload = response.json()
    except ValueError as exc:
        logger.error("Failed to parse GNews.io JSON: %s", exc)
        return []

    articles: list[NewsArticle] = []
    for item in payload.get("articles", []):
        articles.append(
            NewsArticle(
                title=item.get("title", ""),
                link=item.get("url", ""),
                published=item.get("publishedAt", ""),
                content=item.get("description", ""),
                source=item.get("source", {}).get("name", ""),
            )
        )

    logger.info("GNews.io: fetched %d article(s) for query '%s'.", len(articles), query)
    return articles

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

#Follows redirects to resolve the actuals news source URL. 
def resolve_google_news_url(google_url: str) -> str:
    try:
        response = requests.get(
            google_url,
            allow_redirects=True,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (compatible; newsbot/1.0)"}
        )
        return response.url 
    except Exception:
        return google_url  

#Fetching full article content from the url provided in the RSS feed.
def fetch_article_content(url: str) -> str:
    if not url:
        return ""
    if "news.google.com" in url:
        url = resolve_google_news_url(url)

    #Newspaper3k
    if HAS_NEWSPAPER:
        try:
            article = NewsArticle(url, language="en")
            article.download()
            article.parse()
            text = article.text.strip()
            if len(text) >= MIN_CONTENT_LENGTH and "JavaScript" not in text:
                return text
        except Exception as exc:
            logger.debug("newspaper3k failed for %s: %s", url, exc)

    #BeautifulSoup - Fallback
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

#Google news.
def fetch_news_google(
    query: str,
    num_articles: int = 10,
    fetch_full_content: bool = True,
    ) -> list[NewsArticle]:
    rss_url = (
    f"{GOOGLE_NEWS_RSS_URL}"
    f"?q={quote(query)}"
    f"+when:24h"     
    f"&hl=en"
    f"&gl=US"
    f"&ceid=US:en"
    )

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


