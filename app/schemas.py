# app/schemas.py

from pydantic import BaseModel
import enum

class Role(str, enum.Enum):
    user = "user"
    assistant = "assistant"
    tool = "tool"

class ChatMessage(BaseModel):
    role: Role
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]

