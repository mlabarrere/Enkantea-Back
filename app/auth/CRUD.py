from uuid import UUID
from datetime import datetime, timezone
from sqlmodel import select
from fastapi import Depends, Request, HTTPException
import jwt
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

from app.auth.models import (
    PublicAccessTokenPayload,
    InternalAccessTokenPayload,
    RefreshTokenPayload,
    RefreshToken,
    InternalRefreshToken
)
from app.core.config import settings
from app.users.models import UserRead
from app.core.exceptions import InternalError, TokenError, UserNotFoundError
from app.users.CRUD import get_user_by_uuid
from app.core.database import get_db_session

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

TokenDep = Annotated[str, Depends(reusable_oauth2)]


def create_access_token(payload: PublicAccessTokenPayload) -> str:
    try:
        return jwt.encode(
            payload=payload.model_dump(),
            key=settings.TOKEN_SECRET,
            algorithm=settings.TOKEN_ALGORITHM,
        )
    except Exception:
        raise InternalError("Error creating access token")


def decode_access_token(token: str) -> InternalAccessTokenPayload:
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.TOKEN_SECRET,
            algorithms=[settings.TOKEN_ALGORITHM],
            options={"verify_iss": True},
        )
        return InternalAccessTokenPayload(
            user_uuid=UUID(payload["user_uuid"]),
            orga_uuids=[UUID(orga) for orga in payload["orga_uuids"]],
            role=payload["role"],
        )
    except jwt.ExpiredSignatureError as e:
        raise TokenError(f"Token has expired : {e}")
    except jwt.InvalidTokenError as e:
        raise TokenError(f"Invalid token : {e}")
    except Exception as e:
        raise InternalError(f"Error decoding access token : {e}")


async def get_current_user(token: TokenDep) -> UserRead:
    try:
        token_payload = decode_access_token(token)
        user = await get_user_by_uuid(user_uuid=token_payload.user_uuid)
        if user is None:
            raise UserNotFoundError()
        assert user.uuid == token_payload.user_uuid
        return user
    except (TokenError, UserNotFoundError):
        raise
    except Exception:
        raise InternalError("Error retrieving current user")


CurrentUser = Annotated[UserRead, Depends(get_current_user)]


async def verify_organization_access(request: Request, token: TokenDep):
    token_payload = decode_access_token(token)
    assert request is not None

    # Vérifier l'unicité de la clef orga_uuid dans la requête
    request_body = await request.json()
    assert isinstance(request_body, dict)
    assert "orga_uuid" in request_body
    assert isinstance(request_body["orga_uuid"], str)
    orga_uuid = UUID(request_body["orga_uuid"])

    if orga_uuid in token_payload.orga_uuids:
        return

    raise HTTPException(
        status_code=403, detail="User not authorized for this organization"
    )

VerifiedOrganization = Annotated[UUID, Depends(verify_organization_access)]


async def create_refresh_token(user_uuid: UUID) -> str:
    payload = RefreshTokenPayload(user_uuid=str(user_uuid))
    token = jwt.encode(
        payload.model_dump(),
        settings.REFRESH_TOKEN_SECRET,
        algorithm=settings.TOKEN_ALGORITHM,
    )
    refresh_token = RefreshToken(user_uuid=user_uuid, refreshtoken_payload=token)

    with get_db_session() as session:
        session.add(refresh_token)
        session.commit()
        session.refresh(refresh_token)
    return token


def decode_refresh_token(token: str) -> InternalRefreshToken:
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.REFRESH_TOKEN_SECRET,
            algorithms=[settings.TOKEN_ALGORITHM],
        )
        return InternalRefreshToken(
            jti=payload['jti'],
            user_uuid=payload['user_uuid'],
            exp = payload['exp']
            )

    except jwt.ExpiredSignatureError:
        raise TokenError("Refresh token has expired")
    except jwt.InvalidTokenError:
        raise TokenError("Invalid refresh token")
    except Exception:
        raise InternalError("Error decoding refresh token")

async def check_refresh_token_validity(token: str, user_uuid: UUID) -> bool:
    with get_db_session() as session:
        statement = select(RefreshToken).where(
            RefreshToken.user_uuid == user_uuid,
            RefreshToken.refreshtoken_payload == token,
            not RefreshToken.is_revoked,
            RefreshToken.exp > datetime.now(timezone.utc),
        )
        refresh_token = session.exec(statement).first()

        if not refresh_token:
            raise TokenError("Refresh token is invalid, expired, or has been revoked")

        return True


async def revoke_refresh_token(token: str, user_uuid: UUID):
    with get_db_session() as session:
        statement = select(RefreshToken).where(
            RefreshToken.user_uuid == user_uuid,
            RefreshToken.refreshtoken_payload == token,
        )
        refresh_token = session.exec(statement).first()

        if refresh_token:
            refresh_token.is_revoked = True
            session.commit()
            session.refresh(refresh_token)


async def delete_expired_tokens():
    with get_db_session() as session:
        statement = select(RefreshToken).where(
            RefreshToken.exp <= datetime.now(timezone.utc)
        )
        expired_tokens = session.exec(statement).first()
        assert expired_tokens is not None
        for token in expired_tokens:
            session.delete(token)

        session.commit()
