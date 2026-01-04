def build_prompt(context: str, user_query: str) -> str:
    """
    Build the final prompt sent to the LLM.

    Args:
        context: Retrieved RAG context (policies + products)
        user_query: Original user question / email content

    Returns:
        A single formatted prompt string
    """

    system_instructions = (
        "You are a helpful customer support assistant.\n"
        "Use ONLY the information provided in the context to answer.\n"
        "If the context does not contain the answer, say you do not have enough information.\n"
        "Be concise, clear, and professional."
    )

    prompt_parts = [
        "SYSTEM:",
        system_instructions,
        "",
    ]

    if context:
        prompt_parts.extend([
            "CONTEXT:",
            context,
            "",
        ])

    prompt_parts.extend([
        "USER QUESTION:",
        user_query.strip()
    ])

    return "\n".join(prompt_parts)
