from fastapi import APIRouter, Request, HTTPException
from app.users.models import UserCreate, UserRead, UserUpdate
from uuid import UUID

from app.auth.CRUD import CurrentUser
from app.users.CRUD import (
    create_user,
    get_user_by_uuid,
    update_user,
    get_all_orgas_of_user,
)
from app.organisations.models_organisations import OrganisationCreate
from app.organisations.CRUD import create_organisation
from app.organisations.utils import add_user_to_organisation
from app.organisations.models_permissions import UserRole


router = APIRouter()


@router.post("/new", response_model=UserRead, status_code=201)
async def write_user(user_to_create: UserCreate) -> UserRead | None:
    try:
        created_user = await create_user(user_create=user_to_create)
        organisation_details = OrganisationCreate(
            name=f"Organisation de {created_user.last_name}"
        )
        user_orga = await create_organisation(organisation_create=organisation_details)
        _ = await add_user_to_organisation(
            user_uuid=created_user.uuid, orga_uuid=user_orga.uuid, role=UserRole.ADMIN
        )
        return created_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


@router.get("/me", response_model=UserRead, status_code=200)
async def get_current_user_info(current_user: CurrentUser) -> UserRead:
    try:
        return current_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_uuid}", response_model=UserRead, status_code=200)
async def read_user(user_uuid: UUID) -> UserRead | None:
    try:
        user = await get_user_by_uuid(user_uuid=user_uuid)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


@router.patch("/{user_uuid}", response_model=UserRead, status_code=200)
async def patch_user(user_update: UserUpdate) -> UserRead | None:
    try:
        user = await update_user(user_update=user_update)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.get("/me/organisations", response_model=list[UUID], status_code=200)
async def get_user_organisations(request: Request):
    try:
        user_uuid = request.state.user_uuid
        organisations = await get_all_orgas_of_user(user_uuid=user_uuid)
        return organisations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
