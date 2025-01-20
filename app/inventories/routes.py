from fastapi import APIRouter, HTTPException, Query
from uuid import UUID
from app.inventories.models import InventoryCreate, InventoryRead, InventoryUpdate
from app.lots.models import LotRead
from app.inventories import CRUD
from app.core.exceptions import DatabaseOperationError
from app.auth.CRUD import CurrentUser

router = APIRouter()


@router.post("/", response_model=InventoryRead)
async def create_inventory(inventory: InventoryCreate, current_user: CurrentUser):
    try:
        return await CRUD.create_inventory(inventory)
    except DatabaseOperationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{inventory_uuid}", response_model=InventoryRead)
async def get_inventory(inventory_uuid: UUID, current_user: CurrentUser):
    try:
        return await CRUD.get_inventory_by_uuid(inventory_uuid)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{inventory_uuid}", response_model=InventoryRead)
async def update_inventory(
    inventory_uuid: UUID, inventory_update: InventoryUpdate, current_user: CurrentUser
):
    try:
        return await CRUD.update_inventory(inventory_uuid, inventory_update)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseOperationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{inventory_uuid}", response_model=InventoryRead)
async def delete_inventory(inventory_uuid: UUID, current_user: CurrentUser):
    try:
        return await CRUD.delete_inventory(inventory_uuid)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseOperationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/organisation/{orga_uuid}", response_model=list[InventoryRead])
async def get_inventories_of_organisation(
    orga_uuid: UUID,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    try:
        return await CRUD.get_inventories_of_organisation(orga_uuid, skip, limit)
    except DatabaseOperationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{inventory_uuid}/lots", response_model=list[LotRead])
async def get_lots_of_inventory(inventory_uuid: UUID, current_user: CurrentUser):
    try:
        return await CRUD.get_lots_of_inventory(inventory_uuid)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseOperationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{inventory_uuid}/search", response_model=list[LotRead])
async def search_and_filter_lots(
    inventory_uuid: UUID,
    current_user: CurrentUser,
    search_term: str | None = None,
    min_estimate: float | None = None,
    max_estimate: float | None = None,
    category: str | None = None,
):
    try:
        return await CRUD.search_and_filter_lots(
            inventory_uuid, search_term, min_estimate, max_estimate, category
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseOperationError as e:
        raise HTTPException(status_code=400, detail=str(e))
