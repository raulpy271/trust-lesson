
from os import environ


DEBUG = environ.get('DEBUG', 'false').lower() == "true"

REDIS_HOST = environ.get("REDIS_HOST")
REDIS_PORT = environ.get("REDIS_PORT", 6379)
REDIS_PASSWORD = environ.get("REDIS_PASSWORD")
REDIS_SSL = bool(environ.get("REDIS_SSL", False))

DB_DIALECT = environ.get("DB_DIALECT", "postgresql")
DB_DRIVER = environ.get("DB_DRIVER", "psycopg")
DB_HOST = environ.get("DB_HOST")
DB_PORT = environ.get("DB_PORT", 5432)
DB_NAME = environ.get("DB_NAME")
DB_USER = environ.get("DB_USER")
DB_PASSWORD = environ.get("DB_PASSWORD")

TOKEN_EXP = 10 * 60 # Expiration in seconds
TOKEN_REGENERATE = 2 * 60 # Remaining seconds to regenerate new token
JWT_ALGORITHM = 'HS256'
JWT_ISSUER = 'Trust Lesson API'
SCRYPT_SETTINGS = {
    'n': 2 ** 14,
    'r': 8,
    'p': 1
}

if DB_DIALECT == "sqlite":
    # In-memory sqlite
    DB_URL = f"{DB_DIALECT}+{DB_DRIVER}://"
else:
    DB_URL = f"{DB_DIALECT}+{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

