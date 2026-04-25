from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message text")
    session_id: str = Field(..., description="Unique session identifier")
    language: Optional[str] = Field(default="en", description="Language code: en or hi")


class MenuOption(BaseModel):
    id: str
    label: str
    description: str
    prompt: str


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI text response")
    options: List[MenuOption] = Field(default_factory=list, description="Menu options for user")
    session_id: str = Field(..., description="Session identifier")


class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None


class ConversationHistory(BaseModel):
    session_id: str
    messages: List[Message] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "ok"
    database: str = "disconnected"


class ProductInfo(BaseModel):
    name: str
    tagline: str
    description: str
    products: Union[List[Dict[str, Any]], Dict[str, Any]] = Field(default_factory=list)
    company: dict = Field(default_factory=dict)
    greeting: Union[str, Dict[str, str]] = Field(default_factory=dict)
    menu_options: List[MenuOption] = Field(default_factory=list)