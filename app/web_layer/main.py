from fastapi import APIRouter
from app.web_layer.routes.lots import route as get_lot
from app.web_layer.routes.auth import router

api_router = APIRouter()

api_router.include_router(get_lot, prefix="/lots", tags=["lots"])
api_router.include_router(router, prefix= "/users", tags=["users"])