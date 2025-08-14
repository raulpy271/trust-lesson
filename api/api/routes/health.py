from fastapi import APIRouter, Response

import api.health
from api.dto import HealthOut

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/health", response_model=HealthOut)
async def health(response: Response):
    result, status_code = await api.health.health()
    response.status_code = status_code
    return result
