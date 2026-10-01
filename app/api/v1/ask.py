"""
POST /api/v1/ask — skeleton, now with logging and one expected-error case.

Still no LLM, no retrieval, no auth. Phase 13 (RAG Generation) is what
replaces the hardcoded answer with a real, grounded one.

Phase 2 addition: an EXPECTED error case (empty question -> HTTP 400).
This is deliberately different from the global exception handler in
main.py: this is a condition we anticipated and are handling on purpose,
with a specific, meaningful status code and message — not an unhandled
crash caught by a generic safety net.
"""

import logging

from fastapi import APIRouter, HTTPException

from app.schemas.ask import AnswerResponse, QuestionRequest

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ask", response_model=AnswerResponse, tags=["ask"])
def ask_question(request: QuestionRequest) -> AnswerResponse:
    if not request.question.strip():
        # EXPECTED error: we know this can happen, so we handle it
        # explicitly with a specific status code and message.
        logger.warning("Rejected empty question")
        raise HTTPException(status_code=400, detail="question must not be empty")

    logger.info("Received question: %s", request.question)

    return AnswerResponse(
        question=request.question,
        answer="AI response will be implemented later.",
    )
