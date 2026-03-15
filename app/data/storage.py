import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "gold_news"
VECTOR_SIZE = 1024 
QDRANT_PATH = "./qdrant_data"

#Load once on first use
_client: QdrantClient | None = None
_model: SentenceTransformer | None = None

def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(path=QDRANT_PATH)
    return _client

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")
    return _model


def init_collection(recreate: bool = False) -> None:

    client = get_client()
    existing = [c.name for c in client.get_collections().collections]

    if recreate and COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)
        existing.remove(COLLECTION_NAME)

    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

#object to dict
def _article_to_payload(article) -> dict:

    tags = getattr(article, "tags", []) or []
    tag_labels = [t["label"] if isinstance(t, dict) else t for t in tags]

    return {
        "title": article.title,
        "published": article.published,
        "source": article.source,
        "link": article.link,
        "content": (article.content or "")[:500],   # store a preview
        "tags": tag_labels,
        "impact_score": getattr(article, "impact_score", 0),
        "direction": getattr(article, "direction", "neutral"),
    }

#Embed and upsert into Qdrant
def store_articles(articles: list) -> int:

    if not articles:
        return 0

    client = get_client()
    model = get_model()
    init_collection()

    points: list[PointStruct] = []
    for article in articles:
        text = f"{article.title}. {article.content or ''}"
        vector = model.encode(text).tolist()
        payload = _article_to_payload(article)

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=payload,
            )
        )

    #Batch upsert
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    return len(points)


def search_similar(query: str, limit: int = 5) -> list:

    client = get_client()
    model = get_model()
    init_collection()

    query_vector = model.encode(query).tolist()
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
    )

    output = []
    for point in results.points:
        output.append({
            "score": round(point.score, 4),
            **point.payload,
        })
    return output


def close():
    global _client
    if _client is not None:
        _client.close()
        _client = None


#Test code by AI
if __name__ == "__main__":
    from dataclasses import dataclass

    @dataclass
    class _TestArticle:
        title: str = ""
        published: str = ""
        source: str = ""
        link: str = ""
        content: str = ""

    test_articles = [
        _TestArticle(
            title="Federal Reserve held rates steady, gold rallied",
            source="Reuters",
            content="Gold prices surged after the Fed held rates...",
        ),
        _TestArticle(
            title="US CPI inflation comes in hotter than expected",
            source="Bloomberg",
            content="Consumer prices rose 3.5% year over year, above the 3.2% forecast...",
        ),
        _TestArticle(
            title="Tesla announces new gigafactory in Mexico",
            source="CNBC",
            content="Electric vehicle maker Tesla plans to build its next factory...",
        ),
    ]

    for a in test_articles:
        a.tags = []
        a.impact_score = 0
        a.direction = "neutral"

    init_collection(recreate=True)
    count = store_articles(test_articles)
    print(f"Stored {count} articles.")

    for q in ["Fed interest rates?", "Is inflation rising?", "Electric vehicles?"]:
        print(f"\nQuery: {q}")
        for r in search_similar(q, limit=3):
            print(f"  {r['score']:.4f} | {r['title']}")

    close()