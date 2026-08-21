from dataclasses import dataclass
from config import CHUNK_SIZE_CHARS, CHUNK_OVERLAP_CHARS


@dataclass
class Chunk:
    text: str
    chunk_index: int


def split_into_paragraphs(text):
    paras = [p.strip() for p in text.split("\n\n")]
    return [p for p in paras if p]


def chunk_text(text, chunk_size=CHUNK_SIZE_CHARS, overlap=CHUNK_OVERLAP_CHARS):
    paragraphs = split_into_paragraphs(text)
    if not paragraphs:
        return []

    chunks = []
    current = ""

    for para in paragraphs:
        candidate = f"{current}\n\n{para}".strip() if current else para

        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)

        if len(para) <= chunk_size:
            current = para
        else:
            start = 0
            while start < len(para):
                end = min(start + chunk_size, len(para))
                chunks.append(para[start:end])
                if end == len(para):
                    break
                new_start = end - overlap
                if new_start < len(para):
                    space_pos = para.find(" ", new_start)
                    if space_pos != -1 and space_pos - new_start < 30:
                        new_start = space_pos + 1
                start = new_start
            current = ""

    if current:
        chunks.append(current)

    return [Chunk(text=c, chunk_index=i) for i, c in enumerate(chunks)]