Building an AI system that transforms financial news into structured trading intelligence for XAUUSD (Gold) traders.

𝗧𝗵𝗲 𝗣𝗿𝗼𝗯𝗹𝗲𝗺:
A headline like "Fed's Powell signals patience on rate cuts as CPI remains sticky" requires a trader to mentally process: What does this mean for real yields? USD? Gold direction? This takes experience and time.

𝗧𝗵𝗲 𝗦𝗼𝗹𝘂𝘁𝗶𝗼𝗻:
A 7-stage intelligent pipeline:

1️⃣ Fetch → Aggregate news from multiple financial APIs
2️⃣ Filter → Keep only macro-relevant articles
3️⃣ Tag → Label with inflation, fed, yields, dollar, etc.
4️⃣ Score → Rule-based impact scoring
5️⃣ Store → PostgreSQL with full context
6️⃣ Reason → LLM-powered macro analysis
7️⃣ Search → Find similar past events via RAG

𝗖𝘂𝗿𝗿𝗲𝗻𝘁 𝗣𝗿𝗼𝗴𝗿𝗲𝘀𝘀:
✅ Multi-source news ingestion (GNews.io, Marketaux)
✅ Intelligent deduplication
✅ Rule-based macro tagging (40+ patterns)
✅ Impact scoring
✅ PostgreSQL + Qdrant storage
🔜 LLM reasoning qwen2.5:14b(Locally using Ollama)
🔜 RAG retrieval system

𝗧𝗲𝗰𝗵 𝗦𝘁𝗮𝗰𝗸:
Python | NLP | REST APIs | PostgreSQL | Qdrant | LLMs | RAG

𝗪𝗵𝘆 𝗧𝗵𝗶𝘀 𝗠𝗮𝘁𝘁𝗲𝗿𝘀:
After 6+ years trading XAUUSD professionally, I understand the macro relationships that move gold => Fed policy, real yields, DXY, safe-haven flows. This system encodes that domain expertise into AI.
