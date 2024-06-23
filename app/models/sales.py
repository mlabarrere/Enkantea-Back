from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from enum import Enum
from app.models.users import User, UserCreate
from app.models.clients import Client, ClientCreate, ClientUpdate, ClientRead
from app.models.lots import Lot, LotRead, LotCreate, LotUpdate
from app.models.organisations import Organisation, OrganisationCreate, UserRole, UserOrganisationLink

if TYPE_CHECKING:
    from app.models.organisations import Organisation
    from app.models.lots import Lot, LotRead
    from app.models.invoices import Invoice


class SaleStatus(str, Enum):
    DRAFT = "draft"
    PLANNED = "planned"
    ONGOING = "ongoing"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELED = "canceled"


class SaleBase(SQLModel):
    number: int | None = None
    title: str | None = None
    description: str | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    status: SaleStatus = SaleStatus.DRAFT
    location: str | None = None
    fees_percentage: float | None = None
    terms_and_conditions: str | None = None
    catalog_pdf: str | None = None
    illustration_photo: str | None = None
    sale_type: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Sale(SaleBase, table=True):
    id: int = Field(default=None, primary_key=True)
    lots: list["Lot"] = Relationship(back_populates="sale")
    organisation_id: int = Field(default=None, foreign_key="organisation.id")
    organisation: "Organisation" = Relationship(
        back_populates="sales",
        sa_relationship_kwargs={
            "foreign_keys": "Sale.organisation_id",
            "lazy": "selectin",
        },
    )
    invoices: list["Invoice"] = Relationship(back_populates="sale")


class SaleCreate(SaleBase):
    organisation_id: int | None = None
    pass


class SaleRead(SaleBase):
    organisation_id: int
    id: int
    lots: list["LotRead"] | None = None


class SaleUpdate(SaleBase):
    updated_at: datetime = Field(default_factory=datetime.now)


class SaleSettings(SaleBase):
    number: int | None = None
    title: str | None = None
    description: str | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    status: SaleStatus = SaleStatus.DRAFT
    location: str | None = None
    fees_percentage: float | None = None
    terms_and_conditions: str | None = None
    catalog_pdf: str | None = None
    illustration_photo: str | None = None
    sale_type: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
