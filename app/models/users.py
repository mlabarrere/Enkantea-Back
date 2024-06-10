from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from app.models.organisations import Organisation


class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    USER = "user"


class UserOrganisationLink(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    organisation_id: int = Field(foreign_key="organisation.id", primary_key=True)
    role: UserRole
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UserBase(SQLModel):
    email: str = Field(unique=True)
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zipcode: str | None = None
    country: str | None = None
    is_active: bool | None = True
    is_superuser: bool | None = False
    is_staff: bool | None = False


class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    organisation_id: int = Field(default=None, foreign_key="organisation.id")
    organisation: "Organisation" = Relationship(back_populates="users")


class UserCreate(UserBase):
    email: str
    password: str
    first_name: str
    last_name: str


class UserRegister(UserCreate):
    password_confirm: str


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


class UserUpdate(SQLModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zipcode: str | None = None
    country: str | None = None


class UserUpdateMe(SQLModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zipcode: str | None = None
    country: str | None = None


class UpdatePassword(SQLModel):
    old_password: str
    new_password: str
    new_password_confirm: str


class UserPublic(SQLModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    city: str | None = None
    country: str | None = None
