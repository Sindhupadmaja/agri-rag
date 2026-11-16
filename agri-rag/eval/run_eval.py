"""Tiny retrieval/latency eval. Usage: python -m eval.run_eval"""
import json
from pathlib import Path

from src.rag import answer

items = json.loads((Path(__file__).parent / "qa.json").read_text(encoding="utf-8"))
hits, latencies, tokens = 0, [], []

for it in items:
    r = answer(it["question"])
    hit = any(s["source"] == it["expected_source"] for s in r["sources"])
    hits += hit
    latencies.append(r["latency_s"])
    tokens.append(r["tokens"] or 0)
    print(f"{'HIT ' if hit else 'MISS'} {r['latency_s']}s  {it['question'][:70]}")

n = len(items)
print(f"\nRetrieval hit rate: {hits}/{n} = {hits / n:.0%}")
print(f"Avg latency: {sum(latencies) / n:.2f}s | Avg tokens/query: {sum(tokens) / n:.0f}")
