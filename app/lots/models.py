from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from uuid import UUID

if TYPE_CHECKING:
    from app.organisations.models_organisations import Organisation
    from app.sales.models import Sale
    from app.clients.models import Client
    from app.invoices.models import Invoice
    from app.sellers.models import Seller


class LotBase(SQLModel):
    name: str | None = None
    description: str | None = None
    starting_bid: float | None = None
    stock_number: str | None = None
    stock_entry_date: datetime | None = None
    stock_exit_date: datetime | None = None
    location: str | None = None
    category: str | None = None
    photos: str | None = None  # Chemin vers les photos ou URL
    high_estimate: float | None = None
    low_estimate: float | None = None
    reserve_price: float | None = None
    is_reserve_price_net: bool = False
    hammer_price: float | None = None
    tax_rate: float = Field(default=20.0)  # Default to 20% tax rate
    buyer_premium: float | None = None
    seller_premium: float | None = None
    hallmark_fees: float | None = None
    expert_fees: float | None = None
    restoration_fees: float | None = None
    transport_fees: float | None = None
    has_capital_gains_tax: bool = False
    has_copyright: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Lot(LotBase, table=True):
    id: int = Field(default=None, primary_key=True)
    seller_id: int | None = Field(default=None, foreign_key="seller.id")
    seller: "Seller" = Relationship(
        back_populates="lots",
        sa_relationship_kwargs={"foreign_keys": "Lot.seller_id"},
    )
    sale_id: int | None = Field(default=None, foreign_key="sale.id")
    sale: "Sale" = Relationship(back_populates="lots")
    buyer_id: int | None = Field(default=None, foreign_key="client.id")
    buyer: "Client" = Relationship(
        back_populates="lots_buy",
        sa_relationship_kwargs={"foreign_keys": "Lot.buyer_id"},
    )
    orga_uuid: UUID = Field(default=None, foreign_key="organisation.uuid")
    organisation: "Organisation" = Relationship(
        back_populates="lots",
        sa_relationship_kwargs={
            "foreign_keys": "Lot.orga_uuid",
            "lazy": "selectin",
        },
    )
    invoice_id: int | None = Field(default=None, foreign_key="invoice.id")
    invoice: "Invoice" = Relationship(back_populates="lots")


class LotCreate(LotBase):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    seller_id: int | None = None
    sale_id: int | None = None
    buyer_id: int | None = None
    orga_uuid: UUID


class LotRead(LotBase):
    id: int
    # seller: Optional["SellerRead"] = None
    # sale: Optional["Sale"] = None
    # buyer: Optional["ClientRead"] = None
    orga_uuid: UUID
    organisation: "Organisation"


class LotUpdate(SQLModel):
    orga_uuid: UUID
    name: str | None = None
    description: str | None = None
    starting_bid: float | None = None
    stock_number: str | None = None
    stock_entry_date: datetime | None = None
    stock_exit_date: datetime | None = None
    location: str | None = None
    photos: str | None = None
    high_estimate: float | None = None
    low_estimate: float | None = None
    reserve_price: float | None = None
    is_reserve_price_net: bool | None = None
    hammer_price: float | None = None
    buyer_premium: float | None = None
    seller_premium: float | None = None
    hallmark_fees: float | None = None
    expert_fees: float | None = None
    restoration_fees: float | None = None
    transport_fees: float | None = None
    has_capital_gains_tax: bool | None = None
    has_copyright: bool | None = None
    updated_at: datetime = Field(default_factory=datetime.now)
