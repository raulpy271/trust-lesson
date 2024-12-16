
from redis import Redis

from api import settings

_redis = None

def get_default_client():
    global _redis
    if not _redis:
        args = {
            "host": settings.REDIS_HOST,
            "port": settings.REDIS_PORT,
            "password": settings.REDIS_PASSWORD
        }
        _redis = Redis(**args)
    return _redis

