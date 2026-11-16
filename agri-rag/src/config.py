import os

from dotenv import load_dotenv

load_dotenv()


def _req(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name} (see .env.example)")
    return value


OPENAI_ENDPOINT = _req("AZURE_OPENAI_ENDPOINT")
OPENAI_KEY = _req("AZURE_OPENAI_KEY")
OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini")
EMBED_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT", "text-embedding-3-small")
EMBED_DIMS = int(os.getenv("EMBED_DIMS", "1536"))

SEARCH_ENDPOINT = _req("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = _req("AZURE_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX", "agri-rag")
