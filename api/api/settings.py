
from os import environ


DEBUG = environ.get('DEBUG', 'false').lower() == "true"

REDIS_HOST = environ.get("REDIS_HOST")
REDIS_PORT = environ.get("REDIS_PORT")
REDIS_PASSWORD = environ.get("REDIS_PASSWORD")
