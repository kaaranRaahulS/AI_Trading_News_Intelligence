# llm.py

from langchain_openai import ChatOpenAI
from data.storage import search_similar


def get_llm():
    return ChatOpenAI(
        model_name="qwen2.5:14b",
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        temperature=0.7,
    )


def rag_query(question: str, limit: int = 5) -> dict:

    # R — Retrieve
    results = search_similar(question, limit=limit)

    # A — Augment (build context from retrieved articles)
    context_parts = []
    for r in results:
        context_parts.append(
            f"[{r['source']} | {r.get('published', '')} | "
            f"Impact: {r['impact_score']}/10 | Direction: {r['direction']}]\n"
            f"{r['title']}\n{r.get('content', '')}"
        )
    context = "\n\n---\n\n".join(context_parts)

    # G — Generate
    prompt = f"""You are a senior macro analyst specializing in XAUUSD (Gold).
Based on the following recent news articles, answer the question.
Only use information from the provided articles. If the articles don't 
contain enough information, say so.

ARTICLES:
{context}

QUESTION: {question}

ANALYSIS:"""

    llm = get_llm()
    response = llm.invoke(prompt)

    return {
        "answer": response.content,
        "sources": [{"title": r["title"], "score": r["score"]} for r in results],
    }

# At the bottom of llm.py
if __name__ == "__main__":
    result = rag_query("What is driving gold prices right now?")

    print("=== ANALYSIS ===")
    print(result["answer"])

    print("\n=== SOURCES USED ===")
    for s in result["sources"]:
        print(f"  {s['score']:.4f} | {s['title']}")