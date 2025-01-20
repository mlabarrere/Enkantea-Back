from typing import TYPE_CHECKING
from enum import Enum
from sqlmodel import Field, SQLModel
from datetime import datetime
from uuid import uuid4, UUID
from sqlmodel import Relationship


if TYPE_CHECKING:
    from app.organisations.models_organisations import Organisation
    from app.users.models import User


class Role(str, Enum):
    VIEWER = "viewer"
    ACCOUNTANT = "accountant"
    EXTERNAL_OPERATOR = "external_operator"
    OPERATOR = "operator"
    MANAGER = "manager"
    OWNER = "owner"


class Resource(str, Enum):
    ORGANISATION = "organisation"
    CLIENTS = "clients"
    SELLERS = "sellers"
    LOTS = "lots"
    SALES = "sales"
    INVENTORIES = "inventories"
    USERS = "users"
    INVOICES = "invoices"
    MAILS = "mails"


class Permission(str, Enum):
    NONE = "none"
    VIEW = "view"
    EDIT = "edit"
    CREATE = "create"
    DELETE = "delete"


class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"


class UserOrganisationLink(SQLModel, table=True):
    user_uuid: UUID = Field(
        default=uuid4,
        foreign_key="user.uuid",
        primary_key=True,
        nullable=False,
    )
    # user: "User" = Relationship(
    #    back_populates="user",
    #    sa_relationship_kwargs={
    #        "foreign_keys": "user.uuid",
    #        "lazy": "selectin",
    #    },
    # )
    orga_uuid: UUID = Field(
        default=uuid4,
        foreign_key="organisation.uuid",
        primary_key=True,
        nullable=False,
    )
    # organisation: "Organisation" = Relationship(
    #    back_populates="organisation",
    #    sa_relationship_kwargs={
    #        "foreign_keys": "organisation.uuid",
    #        "lazy": "selectin",
    #    },
    # )
    role: UserRole
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UserOrgaRole(SQLModel):
    user_uuid: UUID
    orga_uuid: list[UUID]
    role: Role
