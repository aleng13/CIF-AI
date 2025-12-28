from typing import List

# Hard safety limits (can be tuned later)
MAX_POLICY_CHUNKS = 5
MAX_PRODUCT_CHUNKS = 5
MAX_CHARS_PER_CHUNK = 800


def _clean_chunk(text: str) -> str:
    """
    Normalize and trim a chunk to avoid runaway context.
    """
    text = text.strip().replace("\n", " ")
    if len(text) > MAX_CHARS_PER_CHUNK:
        text = text[:MAX_CHARS_PER_CHUNK] + "..."
    return text


def build_context(
    policy_chunks: List[str],
    product_chunks: List[str]
) -> str:
    """
    Build a structured context string for RAG.

    Output format:

    [POLICIES]
    - ...
    - ...

    [PRODUCTS]
    - ...
    - ...
    """

    sections = []

    if policy_chunks:
        sections.append("[POLICIES]")
        for chunk in policy_chunks[:MAX_POLICY_CHUNKS]:
            sections.append(f"- {_clean_chunk(chunk)}")

    if product_chunks:
        if sections:
            sections.append("")  # blank line between sections
        sections.append("[PRODUCTS]")
        for chunk in product_chunks[:MAX_PRODUCT_CHUNKS]:
            sections.append(f"- {_clean_chunk(chunk)}")

    if not sections:
        return ""

    return "\n".join(sections)
