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


**Output: Live news RAG on 6th of MARCH**

Based on the provided articles, there are conflicting factors influencing gold prices currently:

1. **Bullish Factors**:
   - The Federal Reserve's decision to hold interest rates steady has contributed positively to gold prices.
   - Escalating geopolitical tensions in West Asia and a Middle East war have increased global uncertainty, prompting investors to seek safe-haven assets like gold.

2. **Bearish Factors**:
   - Higher US Treasury yields are putting downward pressure on gold prices because higher yields can reduce demand for non-yielding assets such as gold.
   - A stronger US dollar has also weakened the appeal of gold for international buyers and investors, leading to a decline in gold prices despite rising geopolitical tensions.

The articles indicate that while there is significant safe-haven buying due to global uncertainties, these effects are being countered by higher interest rates and a stronger dollar. The most recent data point from Reuters suggests a bullish trend for gold following the Federal Reserve's rate decision, but other sources like marketaux highlight declines in gold prices despite geopolitical tensions.

**Summary:**
Gold prices are currently influenced by both safe-haven demand due to global conflicts and rising inflation concerns, as well as downward pressures from higher US Treasury yields and a stronger dollar. The overall direction is ambiguous with these opposing forces at play.

**SOURCES USED**
  0.6881 | Federal Reserve held rates steady, gold rallied
  0.6846 | Gold declines as rising yields, firm dollar eclipse safe-haven demand
  0.6846 | Gold declines as rising yields, firm dollar eclipse safe-haven demand
  0.6846 | Gold declines as rising yields, firm dollar eclipse safe-haven demand
  0.6811 | Why are gold and silver rising as gold price surges 1.4% to $5,195 and silver rebounds 3.3% amid Middle East war?
