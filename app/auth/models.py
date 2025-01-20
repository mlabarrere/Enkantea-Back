from sqlmodel import SQLModel
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone
from sqlmodel import Field

from app.core.config import settings
from app.organisations.models_permissions import Role


class PublicAccessTokenPayload(SQLModel):
    # sub	: str #Subject	Identifies the subject of the JWT.
    user_uuid: str  # normalement "sub"
    # aud	: str #Audiences	Identifies the recipients that the JWT is intended for. Each principal intended to process the JWT must identify itself with a value in the audience claim. If the principal processing the claim does not identify itself with a value in the aud claim when this claim is present, then the JWT must be rejected.
    orga_uuids: list[str]  # normalement "aud"
    # Role
    role: str
    # Issuer	Identifies principal that issued the JWT.
    # iss	: str = settings.DOMAIN
    # Expiration Time	Identifies the expiration time on and after which the JWT must not be accepted for processing. The value must be a NumericDate:[9] either an integer or decimal, representing seconds past 1970-01-01 00:00:00Z.
    exp: datetime = Field(
        default_factory=lambda: datetime.now()
        + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    # Not Before	Identifies the time on which the JWT will start to be accepted for processing. The value must be a NumericDate.
    # nbf	: datetime = Field(default_factory=lambda : datetime.now(timezone.utc))
    # Issued at	Identifies the time at which the JWT was issued. The value must be a NumericDate.
    # iat	: datetime = Field(default_factory=lambda : datetime.now(tz=timezone.utc))
    # JWT ID	Case-sensitive unique identifier of the token even among different issuers.
    jti: str = Field(default_factory=lambda: str(uuid4()))
    # Sticky session
    device_fingerprint: str | None = None


class InternalAccessTokenPayload(SQLModel):
    # sub	: str #Subject	Identifies the subject of the JWT.
    user_uuid: UUID  # normalement "sub"
    # aud	: str #Audiences	Identifies the recipients that the JWT is intended for. Each principal intended to process the JWT must identify itself with a value in the audience claim. If the principal processing the claim does not identify itself with a value in the aud claim when this claim is present, then the JWT must be rejected.
    orga_uuids: list[UUID]  # normalement "aud"
    # Role
    role: Role


class RefreshTokenPayload(SQLModel):
    jti: str = Field(default_factory=str, primary_key=True, index=True)
    user_uuid: str = Field(default=str, primary_key=True, index=True)
    # iat: datetime = Field(default_factory=lambda : datetime.now(timezone.utc))
    exp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    iss: str = Field(default=settings.DOMAIN)
    device_fingerprint: str | None = None

class InternalRefreshToken(SQLModel):
    jti: UUID
    user_uuid: UUID
    exp: datetime

class RefreshToken(SQLModel, table=True):
    jti: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_uuid: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    refreshtoken_payload: str
    is_revoked: bool = False
    exp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
