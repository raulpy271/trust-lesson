
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

def hgetall_str(client, key):
    mapping = client.hgetall(key)
    if isinstance(mapping, dict):
        new_mapping = {}
        for k, v in mapping.items():
            if isinstance(v, bytes):
                v = str(v, encoding='utf-8')
            if isinstance(k, bytes):
                new_mapping[str(k, encoding='utf-8')] = v
        return new_mapping
    else:
        return mapping

