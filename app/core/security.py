import jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.models.security import TokenPayload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(payload: TokenPayload) -> str:
    to_encode = payload.model_dump()
    encoded_jwt = jwt.encode(
        payload=to_encode,
        key=settings.SECRET_KEY,
        algorithm=settings.TOKEN_ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(secret=plain_password, hash=hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(secret=password)
