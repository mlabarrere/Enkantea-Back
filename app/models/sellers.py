from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

if TYPE_CHECKING:
    from app.models.organisations import Organisation
    from app.models.lots import Lot


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
    organisation_id: int = Field(default=None, foreign_key="organisation.id")
    organisation: "Organisation" = Relationship(
        back_populates="sellers",
        sa_relationship_kwargs={
            "foreign_keys": "Seller.organisation_id",
            "lazy": "selectin",
        },
    )


class SellerCreate(SellerBase):
    organisation_id: int | None = None
    pass


class SellerRead(SellerBase):
    id: int
    organisation_id: int
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
