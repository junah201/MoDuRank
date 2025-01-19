from decimal import Decimal
from enum import Enum


class Permission(int, Enum):
    USER = 2**0
    ADMIN = 2**3


def has_permission(
    user_permission: int | Decimal, required_permission: Permission
) -> bool:
    if isinstance(user_permission, Decimal):
        user_permission = int(user_permission)

    return user_permission & required_permission.value == required_permission.value
