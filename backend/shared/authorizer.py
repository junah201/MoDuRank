from decimal import Decimal

from shared.permission import Permission, has_permission


def login_required(permission: int | Decimal):
    return has_permission(permission, Permission.USER)


def admin_required(permission: int | Decimal):
    return has_permission(permission, Permission.ADMIN)
