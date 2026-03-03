from news_ingestion import fetch_news_gnewsio, fetch_news_marketaux
from tagger import tag_article
from deduplication import deduplicate_articles
from datetime import date

def display_article(article, index: int):
    print(f"\n{index}. {article.title}")
    print(f"   Published : {article.published}")
    print(f"   Source    : {article.source}")

    if article.link:
        print(f"   Link      : {article.link}")

    if article.content:
        preview = article.content[:200].replace("\n", " ")
        print(f"   Preview   : {preview}...")
    
    if article.tags:
        tag_labels = [t["label"] for t in article.tags]
        print(f"   Tags      : {', '.join(tag_labels)}")


def main():
    
    #Marketaux
    marketaux_articles = fetch_news_marketaux(
        limit=3,
        published_on=date.today(),
    )
    print(f"   Found {len(marketaux_articles)} articles from Marketaux")

    #Gnewsio
    articles = fetch_news_gnewsio(
        query=("gold price OR XAUUSD OR bullion",
        "gold inflation OR gold CPI",
        "gold federal reserve OR gold interest rates",
        "gold treasury yields OR gold dollar"),
        num_articles=10,
    )
    print(f"   Found {len(articles)} articles from GNews.io")

    #Combining 
    all_articles = marketaux_articles + articles
    print(f"   Total articles fetched: {len(all_articles)}")

    #Deduplication
    deduplication_result = deduplicate_articles(all_articles, key="title")
    unique_articles = deduplication_result.unique_articles
    
    print(f"   {deduplication_result.summary()}")
    
    #Tagging
    for article in unique_articles:
        article.tags = tag_article(article.title, article.content or "")
    
    tagged_count = sum(1 for a in unique_articles if a.tags)
    print(f"   Tagged {tagged_count}/{len(unique_articles)} articles")

    print("\n" + "=" * 60)
    print(f"📰 NEWS RESULTS ({len(unique_articles)} articles)")
    print("=" * 60)
    
    for index, article in enumerate(unique_articles, start=1):
        display_article(article, index)

if __name__ == "__main__":
    main()