from uuid import UUID
import jwt
from jwt.exceptions import InvalidTokenError
from typing import Annotated
from pydantic import ValidationError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.CRUD import settings
from app.organisations.models_permissions import Role, Resource
from app.auth.models import PublicAccessTokenPayload, InternalAccessTokenPayload
from app.organisations.models_permissions import UserOrgaRole


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_orga_uuid(token: TokenDep) -> list[UUID]:
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.TOKEN_ALGORITHM],
            verify=True,
            issuer=settings.DOMAIN,
        )
        token_data = InternalAccessTokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    return token_data.orga_uuids


def get_current_UserOrgaRole(token: TokenDep) -> UserOrgaRole:
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.TOKEN_ALGORITHM],
            verify=True,
            issuer=settings.DOMAIN,
        )
        token_data = PublicAccessTokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    return UserOrgaRole(
        user_uuid=token_data.user_uuid,
        orga_uuid=token_data.orga_uuid,
        role=token_data.role,
    )


def has_permission(role: Role, resource: Resource | None, action: str) -> bool:
    permissions = {
        Role.VIEWER: {"view"},
        Role.ACCOUNTANT: {"view", "edit_invoices"},
        Role.EXTERNAL_OPERATOR: {"view", "edit_lots", "edit_sales"},
        Role.OPERATOR: {"view", "edit", "create"},
        Role.MANAGER: {"view", "edit", "create", "delete"},
        Role.OWNER: {"view", "edit", "create", "delete", "manage_users"},
    }

    allowed_actions = permissions.get(role, set())

    if action == "view" and "view" in allowed_actions:
        return True
    if action in ["edit", "create", "delete"] and action in allowed_actions:
        return True
    if action == "manage_users" and "manage_users" in allowed_actions:
        return True

    return False


def permission_required(resource: Resource | None, action: str):
    def decorator(func):
        async def wrapper(
            current_user: AccessTokenPayload = Depends(get_current_UserOrgaRole),
            *args,
            **kwargs,
        ):
            if not has_permission(current_user.role, resource, action):
                raise HTTPException(status_code=403, detail="Permission denied")
            return await func(current_user, *args, **kwargs)

        return wrapper

    return decorator
