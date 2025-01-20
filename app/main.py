from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from fastapi import APIRouter
from app.users.routes import router as users_router
from app.inventories.routes import router as inventories_router
from app.lots.routes import router as lots_router
from app.auth.routes import router as auth_router


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


""" if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True) """

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    # generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
async def read_main():
    return {"msg": "Hello World"}


init_db()


api_router = APIRouter()
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(lots_router, prefix="/lots", tags=["lots"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(
    inventories_router, prefix="/inventories", tags=["inventories"]
)
app.include_router(api_router, prefix=settings.API_V1_STR)
