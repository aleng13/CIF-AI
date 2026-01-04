from typing import List
from sqlalchemy import text
from storage.db import engine  # uses your existing SQLAlchemy engine
from rag.embeddings import embed_query


def search(query: str, top_k: int = 5):
    """
    RAG search entrypoint used by decision.py.

    Returns:
        List[Dict] with keys: text, source
    """

    query_embedding = embed_query(query)

    policy_chunks = vector_search(
        query_embedding=query_embedding,
        sources=["policy"],
        top_k=top_k
    )
    print(f"Chunks from policy: {policy_chunks[:20]}")
    product_chunks = vector_search(
        query_embedding=query_embedding,
        sources=["product"],
        top_k=top_k
    )
    print(f"Chunks from product: {product_chunks[:20]}")
    docs = []

    for chunk in policy_chunks:
        docs.append({
            "text": chunk,
            "source": "policy"
        })

    for chunk in product_chunks:
        docs.append({
            "text": chunk,
            "source": "product"
        })

    return docs

def vector_search(
    query_embedding: list[float],
    sources: List[str],
    top_k: int = 5
) -> List[str]:
    """
    Perform vector similarity search against pgvector.

    Args:
        query_embedding: 768-dim query embedding
        sources: list of document sources (e.g. ["policy"], ["product"], or both)
        top_k: number of chunks to retrieve

    Returns:
        List of chunk content strings
    """

    if not query_embedding or len(query_embedding) != 768:
        raise ValueError("query_embedding must be a 768-dim vector")

    if not sources:
        raise ValueError("sources list cannot be empty")

    sql = text("""
        SELECT dc.content
        FROM document_chunks dc
        JOIN documents d ON dc.document_id = d.id
        WHERE d.is_active = true
          AND d.source = ANY(:sources)
        ORDER BY dc.embedding <-> (:query_embedding)::vector
        LIMIT :top_k
    """)

    with engine.connect() as conn:
        rows = conn.execute(
            sql,
            {
                "query_embedding": query_embedding,
                "sources": sources,
                "top_k": top_k
            }
        ).fetchall()

    return [row[0] for row in rows]
