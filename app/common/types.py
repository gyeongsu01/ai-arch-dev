# Type definitions

from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class UserContext(BaseModel):
    id: str
    role: str
    scopes: List[str] = Field(default_factory=list)


class AskRequest(BaseModel):
    user: UserContext
    question: str


class ToolCall(BaseModel):
    action_id: str
    params: Dict[str, Any] = Field(default_factory=dict)


class GraphState(BaseModel):
    trace_id: str
    user: UserContext
    question: str

    # Agent decision
    tool_call: Optional[ToolCall] = None

    # Tool execution
    tool_result: Optional[Dict[str, Any]] = None

    # Final answer
    answer: Optional[str] = None
