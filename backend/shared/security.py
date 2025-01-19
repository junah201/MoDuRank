import os
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_EXPIRE_MINUTES = 60 * 24 * 7  # one week


def create_access_token(
    data: dict,
    *,
    algorithm: str = ALGORITHM,
    expires_delta: timedelta = timedelta(minutes=JWT_EXPIRE_MINUTES),
) -> str:
    data = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    data.update(
        {
            "exp": expire,
        }
    )

    return jwt.encode(data, key=JWT_SECRET_KEY, algorithm=algorithm)


def verify_access_token(token: str) -> dict:
    return jwt.decode(token, key=JWT_SECRET_KEY, algorithms=[ALGORITHM])


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
