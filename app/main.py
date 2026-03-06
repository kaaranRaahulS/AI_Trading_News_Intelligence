# main.py
from pipeline import run_pipeline
from storage import search_similar, close as close_storage


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
        tag_labels = [t["label"] if isinstance(t, dict) else t for t in article.tags]
        print(f"   Tags      : {', '.join(tag_labels)}")

    if hasattr(article, "impact_score"):
        print(f"   Impact    : {article.impact_score}/10 ({article.direction})")


def run_search_demo():
    demo_queries = [
        "Federal Reserve interest rate decision impact on gold",
        "Inflation data and gold price movement",
        "Geopolitical tensions safe haven demand",
    ]
    print("\n" + "=" * 60)
    print("🔍 SIMILARITY SEARCH")
    print("=" * 60)

    for q in demo_queries:
        results = search_similar(q, limit=3)
        print(f"\n  Query: {q}")
        if not results:
            print("    (no results)")
        for r in results:
            print(f"    {r['score']:.4f} | [{r['impact_score']}/10 {r['direction']}] {r['title']}")


def main():
    #Full pipeline
    articles = run_pipeline()

    #News results
    print("\n" + "=" * 60)
    print(f"📰 NEWS RESULTS ({len(articles)} articles)")
    print("=" * 60)
    for index, article in enumerate(articles, start=1):
        display_article(article, index)

    #Demo Query 
    run_search_demo()

    close_storage()


if __name__ == "__main__":
    main()