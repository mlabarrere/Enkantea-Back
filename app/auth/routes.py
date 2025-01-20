from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.CRUD import (
    create_access_token,
    CurrentUser,
    create_refresh_token,
    decode_refresh_token,
    check_refresh_token_validity,
)
from app.auth.models import PublicAccessTokenPayload
from app.organisations.models_permissions import Role
from app.users.models import UserRead
from app.users.CRUD import get_user_by_email, get_all_orgas_of_user, get_user_by_uuid
from app.core.exceptions import (
    InternalError,
    TokenError,
    UserNotFoundError,
    AuthenticationError,
)
from app.core.config import settings


router = APIRouter()


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return settings.pwd_context.verify(secret=plain_password, hash=hashed_password)
    except Exception:
        raise InternalError("Error during password verification")


@router.get("/")
async def read_main():
    return {"msg": "Hello Auth"}


@router.post("/login", response_model=dict, status_code=200)
async def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = await get_user_by_email(email=form_data.username)
        if not user or not _verify_password(
            plain_password=form_data.password, hashed_password=user.password
        ):
            raise AuthenticationError()

        user_organisations_uuids = await get_all_orgas_of_user(user_uuid=user.uuid)

        access_token_payload = PublicAccessTokenPayload(
            user_uuid=str(user.uuid),
            orga_uuids=[str(org) for org in user_organisations_uuids],
            role=Role.OWNER,
        )

        access_token = create_access_token(access_token_payload)
        refresh_token = await create_refresh_token(user.uuid)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=e.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


@router.post("/login/test-token", response_model=UserRead, status_code=200)
async def test_token(user: CurrentUser):
    try:
        return user
    except TokenError as e:
        raise HTTPException(status_code=401, detail=e.to_dict())
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.to_dict())
    except InternalError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())


@router.post("/refresh", response_model=dict, status_code=200)
async def refresh_access_token(refresh_token: str):
    try:
        refresh_payload = decode_refresh_token(refresh_token)
        user = await get_user_by_uuid(user_uuid=refresh_payload.user_uuid)
        if not user:
            raise UserNotFoundError()

        try:
            assert await check_refresh_token_validity(
                token=refresh_token, user_uuid=user.uuid
            )
        except AssertionError as e:
            raise TokenError(f"Refresh token is invalid or has been revoked : {e}")

        user_organisations_uuids = await get_all_orgas_of_user(user_uuid=user.uuid)

        new_access_token_payload = PublicAccessTokenPayload(
            user_uuid=str(user.uuid),
            orga_uuids=[str(org) for org in user_organisations_uuids],
            role=Role.OWNER,
        )

        new_access_token = create_access_token(new_access_token_payload)

        return {"access_token": new_access_token, "token_type": "bearer"}
    except TokenError as e:
        raise HTTPException(status_code=401, detail=e.to_dict())
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.to_dict())
    except InternalError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
