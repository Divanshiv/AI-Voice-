from fastapi import APIRouter
from app.models.chat_models import HealthResponse
from app.database.mongodb import mongodb


router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    db_status = "connected" if mongodb.connect() else "disconnected"
    return HealthResponse(status="ok", database=db_status)