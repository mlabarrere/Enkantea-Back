from sqlmodel import Field, SQLModel
from datetime import datetime
from uuid import uuid4, UUID


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True, nullable=False)
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    address: str | None = None


class User(UserBase, table=True):
    uuid: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    password: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UserCreate(UserBase):
    email: str
    password: str
    first_name: str | None = None
    last_name: str | None = None


class UserRegister(SQLModel):
    uuid: UUID
    password: str


class UserRead(UserBase):
    uuid: UUID
    created_at: datetime
    updated_at: datetime


class UserUpdate(UserBase):
    uuid: UUID


class UpdatePassword(SQLModel):
    old_password: str
    new_password: str
    new_password_confirm: str


class UserPublic(SQLModel):
    uuid: UUID
    first_name: str | None = None
    last_name: str | None = None
    city: str | None = None
    country: str | None = None
