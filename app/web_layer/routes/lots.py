from app.models.lots import Lot, LotRead
from app.models.users import User, UserRead
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from app.web_layer.deps import CurrentUser, SessionDep

route = APIRouter()

@route.get("/lots/{lot_id}")
def get_lot(lot_id: int, session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100):
    lot = session.query(Lot).filter(Lot.id == lot_id).first()
    if lot is None:
        raise HTTPException(status_code=404, detail="Lot not found")
    return lot