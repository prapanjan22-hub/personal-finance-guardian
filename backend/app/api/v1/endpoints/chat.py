from fastapi import APIRouter
from pydantic import BaseModel
from app.llm_layer.engine import LLMEngine

router = APIRouter()
llm_engine = LLMEngine()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat_with_guardian(request: ChatRequest):
    """
    Chat with the Financial Guardian.
    """
    response = llm_engine.answer_question(request.message, [])
    return {"response": response}
