from enum import Enum
from typing import List, Callable, Any
from fastapi import Depends
from core.exceptions import AuthorizationError
from .auth import get_current_user


class Role(str, Enum):
    ADMIN = "ADMIN"
    ANALYST = "ANALYST"
    VIEWER = "VIEWER"
    API_USER = "API_USER"
    SYSTEM = "SYSTEM"


class Permission(str, Enum):
    READ_TRANSACTIONS = "READ_TRANSACTIONS"
    WRITE_TRANSACTIONS = "WRITE_TRANSACTIONS"
    MANAGE_CASES = "MANAGE_CASES"
    MANAGE_MODELS = "MANAGE_MODELS"
    ADMIN_ACCESS = "ADMIN_ACCESS"
    VIEW_DASHBOARD = "VIEW_DASHBOARD"
    MANAGE_USERS = "MANAGE_USERS"


ROLE_PERMISSIONS = {
    Role.ADMIN: [p for p in Permission],
    Role.ANALYST: [
        Permission.READ_TRANSACTIONS,
        Permission.MANAGE_CASES,
        Permission.VIEW_DASHBOARD,
    ],
    Role.VIEWER: [
        Permission.READ_TRANSACTIONS,
        Permission.VIEW_DASHBOARD,
    ],
    Role.API_USER: [
        Permission.WRITE_TRANSACTIONS,
        Permission.READ_TRANSACTIONS,
    ],
    Role.SYSTEM: [p for p in Permission],
}


def require_role(required_roles: List[Role]) -> Callable:
    async def dependency(current_user: dict = Depends(get_current_user)) -> dict:
        user_role_str = current_user.get("role")
        try:
            user_role = Role(user_role_str)
        except ValueError:
            raise AuthorizationError("Invalid user role")
        
        if user_role not in required_roles:
            raise AuthorizationError("Insufficient role to perform this action")
        
        return current_user
    return dependency


def require_permission(required_permission: Permission) -> Callable:
    async def dependency(current_user: dict = Depends(get_current_user)) -> dict:
        user_role_str = current_user.get("role")
        try:
            user_role = Role(user_role_str)
        except ValueError:
            raise AuthorizationError("Invalid user role")
        
        user_permissions = ROLE_PERMISSIONS.get(user_role, [])
        if required_permission not in user_permissions:
            raise AuthorizationError("Insufficient permissions to perform this action")
            
        return current_user
    return dependency
