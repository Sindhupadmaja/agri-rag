"""Document loading and chunking (no Azure dependencies, easy to unit test)."""
from pathlib import Path

from pypdf import PdfReader


def load_pages(path: Path) -> list[tuple[int, str]]:
    """Return [(page_number, text)] for a PDF, or a single page for .txt/.md."""
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return [(i + 1, (p.extract_text() or "")) for i, p in enumerate(reader.pages)]
    return [(1, path.read_text(encoding="utf-8", errors="ignore"))]


def chunk_text(text: str, size: int = 200, overlap: int = 40) -> list[str]:
    """Word-based sliding window chunking."""
    words = text.split()
    if not words:
        return []
    step = max(size - overlap, 1)
    chunks = []
    for start in range(0, len(words), step):
        piece = words[start : start + size]
        if piece:
            chunks.append(" ".join(piece))
        if start + size >= len(words):
            break
    return chunks
