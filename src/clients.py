from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from openai import AzureOpenAI

from . import config

openai_client = AzureOpenAI(
    azure_endpoint=config.OPENAI_ENDPOINT,
    api_key=config.OPENAI_KEY,
    api_version=config.OPENAI_API_VERSION,
)

_cred = AzureKeyCredential(config.SEARCH_KEY)
index_client = SearchIndexClient(config.SEARCH_ENDPOINT, _cred)
search_client = SearchClient(config.SEARCH_ENDPOINT, config.INDEX_NAME, _cred)


def embed(texts: list[str]) -> list[list[float]]:
    resp = openai_client.embeddings.create(model=config.EMBED_DEPLOYMENT, input=texts)
    return [d.embedding for d in resp.data]
