# Pydantic models
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    agent_used: Optional[str] = None
    tools_used: Optional[List[str]] = []
    processing_time: Optional[float] = None
    message_type: Optional[str] = None

class AgentMessage(BaseModel):
    sender: str
    receiver: str
    type: str
    payload: Dict[str, Any]

class PlanPayload(BaseModel):
    user_message: str
    steps: List[str]
    priority: str
    estimated_duration: str
    context_used: Optional[bool] = False
    llm_generated: Optional[bool] = False

class ExecutionPayload(BaseModel):
    task: str
    result: str
    status: str
    execution_time: str

class KnowledgePayload(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    sources: List[str]
    summary: Optional[str] = ""
    context_used: Optional[bool] = False
    llm_generated: Optional[bool] = False

class MemoryPayload(BaseModel):
    user_id: str
    memory_key: str
    memory_value: Any
    action: str
    category: Optional[str] = "general"
    vector_stored: Optional[bool] = False
    vector_search: Optional[bool] = False
    summary: Optional[str] = ""