from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from enum import Enum
from uuid import uuid4, UUID

if TYPE_CHECKING:
    from app.sales.models import Sale
    from app.clients.models import Client
    from app.lots.models import Lot
    from app.invoices.models import Invoice
    from app.sellers.models import Seller
    from app.inventories.models import Inventory


# CompanyType Enum
class CompanyType(str, Enum):
    EI = "Entrepreneur individuel (EI) (y compris micro-entrepreneur)"
    EURL = "Entreprise unipersonnelle à responsabilité limitée (EURL)"
    SARL = "Société à responsabilité limitée (SARL)"
    SASU = "Société par actions simplifiée unipersonnelle (SASU)"
    SAS = "Société par actions simplifiée (SAS)"
    SA = "Société anonyme (SA)"
    SNC = "Société en nom collectif (SNC)"
    SCS = "Société en commandite simple (SCS)"
    SCA = "Société en commandite par actions (SCA)"


class OrganisationBase(SQLModel):
    # organisation_type: CompanyType | None = None
    name: str
    trigram: str | None = None  # Added trigram
    trade_name: str | None = None
    logo: str | None = None  # URL or path to the logo file
    website: str | None = None
    siren_number: int | None = None
    ape_code: str | None = None
    share_capital: float | None = None
    start_date: datetime | None = None
    registration_date: datetime | None = None
    headquarter_siret_number: str | None = None
    address: str | None = None
    postal_code: str | None = None
    city: str | None = None
    standard_seller_fees: int | None = None
    standard_buyer_fees: int | None = None
    expert_fees: int | None = None


class Organisation(OrganisationBase, table=True):
    uuid: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    sellers: list["Seller"] = Relationship(back_populates="organisation")
    clients: list["Client"] = Relationship(back_populates="organisation")
    sales: list["Sale"] = Relationship(back_populates="organisation")
    lots: list["Lot"] = Relationship(back_populates="organisation")
    invoices: list["Invoice"] = Relationship(back_populates="organisation")
    inventories: list["Inventory"] = Relationship(back_populates="organisation")


class OrganisationCreate(SQLModel):
    name: str


class OrganisationRead(OrganisationBase):
    uuid: UUID
    siren_number: int | None = None
    ape_code: str | None = None
    share_capital: float | None = None
    start_date: datetime | None = None
    registration_date: datetime | None = None
    headquarter_siret_number: int | None = None
    address: str | None = None
    postal_code: str | None = None
    city: str | None = None
    standard_seller_fees: int | None = None
    standard_buyer_fees: int | None = None
    expert_fees: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class OrganisationUpdate(SQLModel):
    organisation_type: CompanyType | None = None
    name: str | None = None
    trigram: str | None = None  # Added trigram
    trade_name: str | None = None
    logo: str | None = None
    website: str | None = None
    siren_number: int | None = None
    ape_code: str | None = None
    share_capital: float | None = None
    start_date: datetime | None = None
    registration_date: datetime | None = None
    headquarter_siret_number: int | None = None
    address: str | None = None
    postal_code: str | None = None
    city: str | None = None
    standard_seller_fees: int | None = None
    standard_buyer_fees: int | None = None
    expert_fees: int | None = None
