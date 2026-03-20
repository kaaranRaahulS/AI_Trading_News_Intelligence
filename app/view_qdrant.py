from qdrant_client import QdrantClient

client = QdrantClient(path="./qdrant_data")

# See how many articles you have
info = client.get_collection("gold_news")
print(f"Total articles: {info.points_count}")

# Browse all stored articles (first 10)
results = client.scroll(
    collection_name="gold_news",
    limit=10,
    with_payload=True,
    with_vectors=False,  # skip vectors, just show the data
)

for point in results[0]:
    p = point.payload
    print(f"\n[{p.get('impact_score', 0)}/10 {p.get('direction', '?')}] {p['title']}")
    print(f"  Source: {p.get('source', '')}")
    print(f"  Tags: {p.get('tags', [])}")

#---------------------#
#Duplicate check
# from qdrant_client import QdrantClient

# client = QdrantClient(path="./qdrant_data")

# # Get all articles
# results = client.scroll(
#     collection_name="gold_news",
#     limit=500,
#     with_payload=True,
#     with_vectors=False,
# )

# # Check for duplicate titles
# titles = [point.payload["title"] for point in results[0]]
# total = len(titles)
# unique = len(set(titles))
# duplicates = total - unique

# print(f"Total articles: {total}")
# print(f"Unique titles: {unique}")
# print(f"Duplicates: {duplicates}")

# # Show which titles are duplicated
# if duplicates > 0:
#     from collections import Counter
#     counts = Counter(titles)
#     print("\nDuplicated articles:")
#     for title, count in counts.items():
#         if count > 1:
#             print(f"  [{count}x] {title}")