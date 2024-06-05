from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from app.models.users import User


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
    company_type: CompanyType | None = None
    company_name: str | None = None
    company_trigram: str | None = None  # Added trigram
    trade_name: str | None = None
    logo: str | None = None  # URL or path to the logo file
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


class Organisation(OrganisationBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    users: list["User"] | None = Relationship(back_populates="organisation")
    # clients: list['Client'] | None = Relationship(back_populates='organisation')
    # sales: list['Sale'] | None = Relationship(back_populates='organisation')
    # lots: list['Lot'] | None = Relationship(back_populates='organisation')
    # invoices: list['Invoice'] | None = Relationship(back_populates='organisation')
    # payments: list['Payment'] | None = Relationship(back_populates='organisation')


class OrganisationCreate(OrganisationBase):
    company_name: str


class OrganisationRead(OrganisationBase):
    id: int | None = None
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
    company_type: CompanyType | None = None
    company_name: str | None = None
    company_trigram: str | None = None  # Added trigram
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
