# Agri RAG – bilingual (EN/FR) RAG on Azure

Small retrieval-augmented generation demo using **Azure OpenAI** (embeddings + chat) and **Azure AI Search** (hybrid keyword + vector retrieval), served via **FastAPI** and containerized with Docker.

```
data/*.pdf -> chunk (200 words, 40 overlap) -> embeddings (text-embedding-3-small)
           -> Azure AI Search index (HNSW vector + BM25)

question -> embed -> hybrid search (top-k) -> grounded prompt -> gpt-4o-mini -> answer + citations
```

## Features
- Hybrid retrieval (BM25 + vector) in Azure AI Search
- Answers in the question's language (English/French), with `[n]` citations to file + page
- "I don't know" fallback when context lacks the answer (hallucination guard, temperature 0)
- Eval script: retrieval hit rate, latency, tokens per query
- REST API (`POST /ask`), minimal web UI at `/`, Dockerfile

## 1. Provision Azure (Azure CLI)
Names must be globally unique; model availability varies by region, so check in Azure AI Foundry if a command fails.
```bash
RG=rg-agri-rag; LOC=canadaeast
az group create -n $RG -l $LOC

# Azure OpenAI
az cognitiveservices account create -n <aoai-name> -g $RG -l $LOC --kind OpenAI --sku S0
az cognitiveservices account deployment create -n <aoai-name> -g $RG \
  --deployment-name gpt-4o-mini --model-name gpt-4o-mini --model-version "2024-07-18" \
  --model-format OpenAI --sku-name GlobalStandard --sku-capacity 10
az cognitiveservices account deployment create -n <aoai-name> -g $RG \
  --deployment-name text-embedding-3-small --model-name text-embedding-3-small --model-version "1" \
  --model-format OpenAI --sku-name Standard --sku-capacity 10

# Azure AI Search (free tier: 1 per subscription)
az search service create -n <search-name> -g $RG --sku free -l $LOC

# Keys
az cognitiveservices account keys list -n <aoai-name> -g $RG
az search admin-key show --service-name <search-name> -g $RG
```
Delete everything afterwards to avoid cost: `az group delete -n rg-agri-rag`.

## 2. Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill in endpoints + keys
# put a few public AAFC / open.canada.ca PDFs (EN + FR) in ./data
python -m src.ingest
uvicorn src.app:app --reload   # http://localhost:8000
python -m eval.run_eval        # after editing eval/qa.json
```

## 3. Docker
```bash
docker build -t agri-rag .
docker run --env-file .env -p 8000:8000 agri-rag
```

## Responsible AI notes
- Answers restricted to retrieved context; explicit refusal when unsupported
- Citations let users verify every claim
- Keys via env vars (never committed); production would use managed identity + Key Vault
- Use only public, non-sensitive documents

## Possible extensions
Azure Container Apps deployment, managed identity auth, semantic ranker, a tool-using agent step (decide when to retrieve), Azure AI Search integrated vectorization.
