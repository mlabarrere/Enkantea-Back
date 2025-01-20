from uuid import UUID
from typing import List
from fastapi import APIRouter, HTTPException, Query, Depends

from app.lots.models import LotCreate, LotRead, LotUpdate
from app.lots.utils import create, get, update, delete, get_lots_of_organization
from app.auth.CRUD import verify_organization_access


router = APIRouter(dependencies=[Depends(verify_organization_access)])


@router.post("/new", response_model=LotRead)
async def create_lot(lot_create: LotCreate):
    try:
        return await create(lot_data=lot_create)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{lot_id}", response_model=LotRead)
async def get_lot(lot_id: int):
    try:
        return await get(lot_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Lot not found")


@router.get("/organization/{orga_uuid}", response_model=List[LotRead])
async def list_lots(
    orga_uuid: UUID, skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=100)
):
    try:
        return await get_lots_of_organization(
            orga_uuid=orga_uuid, skip=skip, limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{lot_id}", response_model=LotRead)
async def update_lot(lot_update: LotUpdate):
    try:
        return await update(lot_update)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{lot_id}", response_model=LotRead)
async def delete_lot(lot_id: int):
    try:
        return await delete(lot_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
