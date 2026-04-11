"""Chat endpoints — main chat and domain-specific chat."""
from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    session_id: str
    user_id: str
    message: str


class DomainChatRequest(BaseModel):
    session_id: str
    user_id: str
    message: str
    domain: str


class ChatResponse(BaseModel):
    role: str = "assistant"
    content: str
    timestamp: str


@router.post("/chat")
async def send_message(req: ChatRequest) -> ChatResponse:
    from runner import run_agent

    response = await run_agent(
        session_id=req.session_id,
        user_id=req.user_id,
        message=req.message,
    )
    return ChatResponse(
        content=response,
        timestamp=datetime.now(timezone.utc).strftime("%H:%M"),
    )


@router.post("/chat/domain")
async def send_domain_message(req: DomainChatRequest) -> ChatResponse:
    from runner import run_agent

    prefixed = f"[{req.domain.title()} context] {req.message}"
    response = await run_agent(
        session_id=req.session_id,
        user_id=req.user_id,
        message=prefixed,
    )
    return ChatResponse(
        content=response,
        timestamp=datetime.now(timezone.utc).strftime("%H:%M"),
    )
