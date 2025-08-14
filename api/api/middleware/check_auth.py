from datetime import datetime
from http import HTTPStatus

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Response
from starlette.middleware.base import BaseHTTPMiddleware

from api import settings
from api.redis import get_default_client, hgetall_str
from api.auth import generate_new_token
from api.utils import parse_bearer


class CheckAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if self.should_be_logged(request):
            logged, token, mapping = self.verify_token(request)
            request.state.logged = logged
            request.state.token = token
            if logged:
                response = await call_next(request)
                self.add_logged_headers(response, token, mapping)
            else:
                response = Response(status_code=HTTPStatus.UNAUTHORIZED)
        else:
            response = await call_next(request)
        return response

    def should_be_logged(self, request):
        return "/logged/" in request.url.path

    def verify_token(self, request):
        authorization = request.headers.get("Authorization")
        if authorization:
            token = parse_bearer(authorization)
            if token:
                redis = get_default_client()
                mapping = hgetall_str(redis, token)
                if (
                    mapping
                    and mapping.get("password_hash")
                    and mapping.get("email")
                    and mapping.get("id")
                ):
                    try:
                        jwt.decode(
                            token,
                            mapping["password_hash"],
                            issuer=settings.JWT_ISSUER,
                            audience=mapping["email"],
                            algorithms=[settings.JWT_ALGORITHM],
                        )
                    except InvalidTokenError:
                        return False, None, None
                    return True, token, mapping
        return False, None, None

    def add_logged_headers(self, response, token, mapping):
        redis = get_default_client()
        exp_s = redis.ttl(token)
        exp_ts = int(datetime.now().timestamp() + exp_s)
        if exp_s <= settings.TOKEN_REGENERATE:
            token, exp_ts = generate_new_token(token, mapping)
        response.headers["Token"] = token
        response.headers["Token-Expiration"] = str(exp_ts)
