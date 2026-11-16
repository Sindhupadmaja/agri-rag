"""Ingest documents in ./data into Azure AI Search.

Usage: python -m src.ingest [data_dir]
"""
import re
import sys
from pathlib import Path

from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)

from . import config
from .chunking import chunk_text, load_pages
from .clients import embed, index_client, search_client


def create_index() -> None:
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="source", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="page", type=SearchFieldDataType.Int32, filterable=True),
        SearchField(
            name="embedding",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=config.EMBED_DIMS,
            vector_search_profile_name="hnsw-profile",
        ),
    ]
    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="hnsw")],
        profiles=[VectorSearchProfile(name="hnsw-profile", algorithm_configuration_name="hnsw")],
    )
    index_client.create_or_update_index(
        SearchIndex(name=config.INDEX_NAME, fields=fields, vector_search=vector_search)
    )


def main(data_dir: str = "data") -> None:
    create_index()
    files = [p for p in Path(data_dir).iterdir() if p.suffix.lower() in {".pdf", ".txt", ".md"}]
    if not files:
        sys.exit(f"No .pdf/.txt/.md files found in {data_dir}/")

    docs = []
    for path in files:
        safe = re.sub(r"[^A-Za-z0-9_-]", "_", path.stem)
        for page, text in load_pages(path):
            for n, chunk in enumerate(chunk_text(text)):
                docs.append(
                    {"id": f"{safe}-p{page}-c{n}", "content": chunk, "source": path.name, "page": page}
                )

    print(f"{len(docs)} chunks from {len(files)} files; embedding...")
    for i in range(0, len(docs), 16):
        batch = docs[i : i + 16]
        for d, vec in zip(batch, embed([d["content"] for d in batch])):
            d["embedding"] = vec
        search_client.upload_documents(batch)
    print("Done.")


if __name__ == "__main__":
    main(*sys.argv[1:2])
