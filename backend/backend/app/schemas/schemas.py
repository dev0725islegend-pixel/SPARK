from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

class ConversationCreate(BaseModel):
    title: Optional[str]

class ConversationOut(BaseModel):
    id: UUID
    user_id: UUID
    title: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    last_message_at: Optional[datetime]

    class Config:
        orm_mode = True

class MessageCreate(BaseModel):
    content: str

class MessageOut(BaseModel):
    id: UUID
    conversation_id: UUID
    sender: str
    content: str
    metadata: Optional[dict]
    created_at: Optional[datetime]

    class Config:
        orm_mode = True
