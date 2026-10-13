from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """
    What we return for the current user (GET /api/v1/auth/me).

    Deliberately does NOT include password_hash — response models don't
    just document output, they also act as an allowlist: even if a route
    accidentally returned the full User ORM object, FastAPI would still
    only serialize the fields declared here.
    """
    id: int
    email: str
    name: str
    organization_id: int

    # Lets this model be built directly from a SQLAlchemy User object
    # (model.id, model.email, ...) instead of requiring a dict.
    model_config = {"from_attributes": True}
