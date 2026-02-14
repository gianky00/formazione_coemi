from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    response: str


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Any:
    """
    Chat endpoint using Gemini Flash with RAG context.
    """
    try:
        # 1. Build Context (with user message for smart employee search)
        context = chat_service.get_rag_context(db, current_user, request.message)

        # 2. Call AI
        # Convert Pydantic history to dict list
        history_dicts = [h.model_dump() for h in request.history]

        reply = chat_service.chat_with_intelleo(request.message, history_dicts, context)

        return ChatResponse(response=reply)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
