"""Retrieval + grounded generation."""
import time

from azure.search.documents.models import VectorizedQuery

from . import config
from .clients import embed, openai_client, search_client

SYSTEM_PROMPT = """You are a helpful assistant answering questions from the provided context only.
Rules:
- Answer in the same language as the question (English or French).
- Cite sources inline as [1], [2] matching the numbered context passages.
- If the context does not contain the answer, say you don't know in the question's language. Do not guess.
- Be concise."""


def retrieve(question: str, k: int = 4) -> list[dict]:
    """Hybrid search: keyword (BM25) + vector, fused by Azure AI Search."""
    vq = VectorizedQuery(vector=embed([question])[0], k_nearest_neighbors=k, fields="embedding")
    results = search_client.search(
        search_text=question, vector_queries=[vq], top=k, select=["content", "source", "page"]
    )
    return [
        {"content": r["content"], "source": r["source"], "page": r["page"], "score": r["@search.score"]}
        for r in results
    ]


def answer(question: str, k: int = 4) -> dict:
    t0 = time.perf_counter()
    passages = retrieve(question, k)
    context = "\n\n".join(
        f"[{i}] ({p['source']}, p.{p['page']})\n{p['content']}" for i, p in enumerate(passages, 1)
    )
    resp = openai_client.chat.completions.create(
        model=config.CHAT_DEPLOYMENT,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )
    return {
        "answer": resp.choices[0].message.content,
        "sources": [{"n": i, "source": p["source"], "page": p["page"]} for i, p in enumerate(passages, 1)],
        "latency_s": round(time.perf_counter() - t0, 2),
        "tokens": resp.usage.total_tokens if resp.usage else None,
    }
