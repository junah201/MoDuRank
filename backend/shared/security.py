import os

from passlib.context import CryptContext

ALGORITHM = "HS256"
PASSWORD_SALT = os.environ.get("PASSWORD_SALT", "modurank")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(f"{password}{PASSWORD_SALT}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(f"{plain_password}{PASSWORD_SALT}", hashed_password)
