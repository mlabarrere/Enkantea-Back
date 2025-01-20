from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from uuid import UUID

if TYPE_CHECKING:
    from app.organisations.models_organisations import Organisation
    from app.lots.models import Lot


class SellerBase(SQLModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zipcode: str | None = None
    country: str | None = None
    company: str | None = None
    professional: bool = False


class Seller(SellerBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    lots: list["Lot"] | None = Relationship(
        back_populates="seller",
        sa_relationship_kwargs={"foreign_keys": "Lot.seller_id", "lazy": "selectin"},
    )
    orga_uuid: UUID = Field(
        default=None, foreign_key="organisation.uuid", nullable=False
    )
    organisation: "Organisation" = Relationship(
        back_populates="sellers",
        sa_relationship_kwargs={
            "foreign_keys": "Seller.orga_uuid",
            "lazy": "selectin",
        },
    )


class SellerCreate(SellerBase):
    orga_uuid: UUID | None = None
    pass


class SellerRead(SellerBase):
    id: int
    orga_uuid: UUID
    created_at: datetime
    updated_at: datetime


class SellerUpdate(SQLModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zipcode: str | None = None
    country: str | None = None
    company: str | None = None
    professional: bool = False
