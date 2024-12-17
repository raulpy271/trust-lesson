
from os import environ


DEBUG = environ.get('DEBUG', 'false').lower() == "true"

REDIS_HOST = environ.get("REDIS_HOST")
REDIS_PORT = environ.get("REDIS_PORT", 6379)
REDIS_PASSWORD = environ.get("REDIS_PASSWORD")

DB_HOST = environ.get("DB_HOST")
DB_PORT = environ.get("DB_PORT", 5432)
DB_NAME = environ.get("DB_NAME")
DB_USER = environ.get("DB_USER")
DB_PASSWORD = environ.get("DB_PASSWORD")
DB_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

