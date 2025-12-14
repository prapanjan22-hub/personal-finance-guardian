from fastapi import APIRouter
from app.api.v1.endpoints import analysis, chat, regime

api_router = APIRouter()
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(regime.router, prefix="/regime", tags=["regime"])

