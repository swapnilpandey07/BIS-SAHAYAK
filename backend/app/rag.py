import logging
from typing import Optional

from backend.app.config import settings
from backend.app.schemas import AskRequest, AskResponse
from backend.app.retrieval import retrieve_relevant_chunks, format_context_for_prompt
from backend.app.prompts import SYSTEM_PROMPT, RAG_PROMPT_TEMPLATE
from backend.app.llm import generate_llm_response

logger = logging.getLogger("bis_rag")

FALLBACK_REFUSAL = "I could not verify this information from the available BIS documents."


def answer_bis_question(request: AskRequest) -> AskResponse:
    """
    End-to-end RAG pipeline:
    1. Retrieve relevant BIS document chunks & extract citations
    2. Guardrail check: if no relevant documents match, refuse immediately
    3. Build context & strictly prompt Gemini LLM
    4. Return grounded answer with verified source citations
    """
    question = request.question.strip()
    if not question:
        return AskResponse(
            question="",
            answer="Please enter a valid question regarding Bureau of Indian Standards (BIS).",
            sources=[],
            retrieved_chunks=0,
            model_used=settings.GEMINI_MODEL,
            is_grounded=True
        )

    # 1. Retrieve chunks
    chunks, citations = retrieve_relevant_chunks(
        query=question,
        top_k=request.top_k,
        category_filter=request.category_filter
    )

    # 2. Strict Grounding Guardrail
    if not chunks:
        logger.info(f"No relevant chunks found for question: '{question}'. Returning refusal.")
        return AskResponse(
            question=question,
            answer=FALLBACK_REFUSAL,
            sources=[],
            retrieved_chunks=0,
            model_used=settings.GEMINI_MODEL,
            is_grounded=True
        )

    # 3. Format Context and Prompt
    context_str = format_context_for_prompt(chunks)
    rag_prompt = RAG_PROMPT_TEMPLATE.format(
        context_str=context_str,
        question=question
    )

    # 4. Generate LLM Answer
    raw_answer = generate_llm_response(
        prompt=rag_prompt,
        system_instruction=SYSTEM_PROMPT,
        temperature=0.1
    )

    # If answer explicitly says unverified, clear sources to avoid false associations
    if FALLBACK_REFUSAL.lower() in raw_answer.lower() and len(raw_answer.split()) < 20:
        citations = []

    return AskResponse(
        question=question,
        answer=raw_answer,
        sources=citations,
        retrieved_chunks=len(chunks),
        model_used=settings.GEMINI_MODEL,
        is_grounded=True
    )
