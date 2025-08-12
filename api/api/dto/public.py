from pydantic import BaseModel


class HealthOut(BaseModel):
    database_healthy: bool | None = None
    database_error: str | None = None
    redis_healthy: bool | None = None
    redis_error: str | None = None
    storage_healthy: bool | None = None
    storage_error: str | None = None
