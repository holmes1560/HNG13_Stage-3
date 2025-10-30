# models/a2a.py
# This file defines the exact structure of the A2A JSON-RPC messages.
# We are copying the relevant parts from the blog post guide.

from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any
from uuid import uuid4

class MessagePart(BaseModel):
    kind: Literal["text", "data", "file"]
    text: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    file_url: Optional[str] = None

class A2AMessage(BaseModel):
    kind: Literal["message"] = "message"
    role: Literal["user", "agent", "system"]
    parts: List[MessagePart]
    messageId: str = Field(default_factory=lambda: str(uuid4()))
    
class MessageParams(BaseModel):
    message: A2AMessage

class JSONRPCRequest(BaseModel):
    jsonrpc: Literal["2.0"]
    id: str
    method: Literal["message/send", "execute"]
    params: MessageParams

# We will simplify the response for our agent. 
# We just need to send a simple text message back.
class JSONRPCResponse(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    id: str
    result: A2AMessage