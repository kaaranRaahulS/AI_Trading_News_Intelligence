from datetime import date
from news_ingestion import fetch_news_gnewsio, fetch_news_marketaux
from tagger import tag_article
from deduplication import deduplicate_articles
from scoring import calculate_impact_score
from storage import init_collection, store_articles


def run_pipeline() -> list:

    #Fetch
    marketaux_articles = fetch_news_marketaux(
        limit=3,
        published_on=date.today(),
    )
    print(f"   Found {len(marketaux_articles)} articles from Marketaux")

    gnews_articles = fetch_news_gnewsio(
        query=("gold price OR XAUUSD OR bullion",
               "gold inflation OR gold CPI",
               "gold federal reserve OR gold interest rates",
               "gold treasury yields OR gold dollar"),
        num_articles=10,
    )
    print(f"   Found {len(gnews_articles)} articles from GNews.io")

    all_articles = marketaux_articles + gnews_articles
    print(f"   Total articles fetched: {len(all_articles)}")

    #Deduplicate
    dedup_result = deduplicate_articles(all_articles, key="title")
    unique_articles = dedup_result.unique_articles
    print(f"   {dedup_result.summary()}")

    #Tag
    for article in unique_articles:
        article.tags = tag_article(article.title, article.content or "")

    tagged_count = sum(1 for a in unique_articles if a.tags)
    print(f"   Tagged {tagged_count}/{len(unique_articles)} articles")

    #Score
    for article in unique_articles:
        score, direction = calculate_impact_score(article)
        article.impact_score = score
        article.direction = direction

    unique_articles.sort(key=lambda a: a.impact_score, reverse=True)
    print(f"   Scored {len(unique_articles)} articles")

    #Store
    init_collection()
    stored = store_articles(unique_articles)
    print(f"   Stored {stored} articles in Qdrant")

    return unique_articles