#This is to test the working of rag pipeline.
import os
from groq import Groq

from rag.embeddings import embed_query
from rag.search import vector_search
from rag.context import build_context
from rag.prompt import build_prompt


# Initialize Groq client once
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def rag_answer(user_query: str) -> str:
    """
    End-to-end RAG pipeline:
    - Embed query
    - Retrieve policy + product context
    - Build prompt
    - Call Groq
    """

    if not user_query or not user_query.strip():
        raise ValueError("user_query cannot be empty")

    # 1. Embed query
    query_embedding = embed_query(user_query)

    # 2. Retrieve context
    policy_chunks = vector_search(
        query_embedding=query_embedding,
        sources=["policy"],
        top_k=3
    )

    product_chunks = vector_search(
        query_embedding=query_embedding,
        sources=["product"],
        top_k=3
    )

    # 3. Build context
    context = build_context(
        policy_chunks=policy_chunks,
        product_chunks=product_chunks
    )

    # 4. Build prompt
    prompt = build_prompt(
        context=context,
        user_query=user_query
    )

    # 5. Call Groq
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=500
    )

    return completion.choices[0].message.content.strip()

