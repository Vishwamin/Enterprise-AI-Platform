"""
Pydantic models for the /api/v1/ask endpoint.

Splitting schemas into their own module (separate from the route function)
is a deliberate separation-of-concerns choice: the "shape of the data"
should be readable/reusable independently of "what the endpoint does."
"""

from pydantic import BaseModel


class QuestionRequest(BaseModel):
    """What a client must send us."""
    question: str


class AnswerResponse(BaseModel):
    """
    What we send back.

    Declaring this explicitly (instead of just returning a dict) lets
    FastAPI validate our OWN output, document it in /docs, and strip
    out any accidental extra fields before they reach the client.
    """
    question: str
    answer: str
