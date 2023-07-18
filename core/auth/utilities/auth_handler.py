from datetime import datetime, timedelta, timezone

import jwt
from fastapi.security import HTTPBearer
from passlib.context import CryptContext

from core.config import settings
from core.exception import (
    EncodeTokenError,
    ExpiredSignatureError,
    InvalidScopeTokenError,
    InvalidTokenError,
)


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = settings.SECRET

    @classmethod
    def get_password_hash(cls, password):
        return cls.pwd_context.hash(password)

    @classmethod
    def verify_password(cls, plain_password, hashed_password):
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def encode_token(cls, email, scope, ttl):
        exp = datetime.now(timezone.utc) + timedelta(**ttl)
        try:
            payload = {
                "exp": exp,
                "iat": datetime.now(timezone.utc),
                "scope": scope,
                "sub": email,
            }
            return jwt.encode(payload, cls.secret, algorithm="HS256")
        except:
            raise EncodeTokenError()

    @classmethod
    def decode_token(cls, token, scope):
        try:
            payload = jwt.decode(token, cls.secret, algorithms=["HS256"])
            if payload["scope"] != scope:
                raise InvalidScopeTokenError()
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise ExpiredSignatureError()
        except jwt.InvalidTokenError:
            raise InvalidTokenError()

    @classmethod
    def refresh_token(cls, refresh_token):
        email = cls.decode_token(refresh_token, "refresh_token")
        return cls.encode_token(email, "access_token", {"days": 0, "hours": 2})
