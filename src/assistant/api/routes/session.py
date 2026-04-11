"""Session management endpoints."""
import uuid
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["session"])


class SessionResponse(BaseModel):
    session_id: str
    user_id: str


@router.post("/session/init")
async def init_session() -> SessionResponse:
    return SessionResponse(
        session_id=str(uuid.uuid4()),
        user_id="default_user",
    )
