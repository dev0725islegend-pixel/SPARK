from fastapi import APIRouter, Depends, HTTPException, status, Request
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session
from backend.app.core.deps import get_db, get_current_user
from backend.app.schemas.schemas import MessageCreate, MessageOut, ConversationCreate, ConversationOut
from backend.app.db import models
from backend.app.services.ai_service import AIService
from typing import Generator

router = APIRouter()
ai_service = AIService()

@router.post("/", response_model=ConversationOut)
def create_conversation(inp: ConversationCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    conv = models.Conversation(user_id=user.id, title=inp.title)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv

@router.get("/", response_model=list[ConversationOut])
def list_conversations(db: Session = Depends(get_db), user=Depends(get_current_user)):
    convs = db.query(models.Conversation).filter(models.Conversation.user_id == user.id).order_by(models.Conversation.last_message_at.desc()).all()
    return convs

@router.get("/{conversation_id}")
def get_conversation(conversation_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id, models.Conversation.user_id == user.id).first()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    messages = db.query(models.Message).filter(models.Message.conversation_id == conv.id).order_by(models.Message.created_at.asc()).all()
    return {"conversation": conv, "messages": messages}

@router.post("/{conversation_id}/messages")
def post_message(conversation_id: str, msg: MessageCreate, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # store user message
    conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id, models.Conversation.user_id == user.id).first()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    user_msg = models.Message(conversation_id=conv.id, sender=models.SenderEnum.user, content=msg.content)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)
    conv.last_message_at = user_msg.created_at
    db.add(conv)
    db.commit()
    # return streaming SSE response that streams assistant tokens
    async def event_generator():
        # stream tokens from AI service
        assistant_content_chunks = []
        try:
            for chunk in ai_service.stream_response(prompt=msg.content):
                assistant_content_chunks.append(chunk)
                yield {"event": "message", "data": chunk}
            # after streaming finished, persist assistant message
            assistant_full = "".join(assistant_content_chunks)
            assistant_msg = models.Message(conversation_id=conv.id, sender=models.SenderEnum.assistant, content=assistant_full)
            db.add(assistant_msg)
            db.commit()
            yield {"event": "done", "data": ""}
        except Exception as e:
            yield {"event": "error", "data": str(e)}

    return EventSourceResponse(event_generator())

@router.post("/{conversation_id}/regenerate")
def regenerate(conversation_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # get last user message and regenerate
    conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id, models.Conversation.user_id == user.id).first()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    last_user = db.query(models.Message).filter(models.Message.conversation_id == conv.id, models.Message.sender==models.SenderEnum.user).order_by(models.Message.created_at.desc()).first()
    if not last_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No user message to regenerate")
    # stream same as above
    async def event_generator():
        chunks = []
        try:
            for chunk in ai_service.stream_response(prompt=last_user.content):
                chunks.append(chunk)
                yield {"event": "message", "data": chunk}
            assistant_full = "".join(chunks)
            assistant_msg = models.Message(conversation_id=conv.id, sender=models.SenderEnum.assistant, content=assistant_full)
            db.add(assistant_msg)
            db.commit()
            yield {"event": "done", "data": ""}
        except Exception as e:
            yield {"event": "error", "data": str(e)}
    return EventSourceResponse(event_generator())
