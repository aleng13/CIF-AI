import os
from nomic import embed
from dotenv import load_dotenv

load_dotenv()

# Nomic Embed V1 is natively 768 dimensions
EMBEDDING_DIM = 768

def embed_query(text: str, is_search_query: bool = True) -> list[float]:
    """
    Convert input text into a Nomic vector embedding.
    """
    if not text or not text.strip():
        raise ValueError("Cannot embed empty text")

    # Use 'search_query' for user questions and 'search_document' for DB indexing
    task = 'search_query' if is_search_query else 'search_document'

    # Ensure your NOMIC_API_KEY is set in your .env file
    output = embed.text(
        texts=[text],
        model='nomic-embed-text-v1',
        task_type=task
    )

    return output['embeddings'][0]