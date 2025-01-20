from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timedelta
from enum import Enum
import hashlib
from uuid import UUID

if TYPE_CHECKING:
    from app.organisations.models_organisations import Organisation
    from app.sales.models import Sale
    from app.clients.models import Client
    from app.lots.models import LotRead, Lot


# Enum for payment status
class PaymentStatus(str, Enum):
    PAID = "paid"
    PENDING = "pending"
    OVERDUE = "overdue"
    PARTIALLY_PAID = "partially_paid"


class InvoiceBase(SQLModel):
    client_id: int = Field(default=None, foreign_key="client.id")
    sale_id: int
    number: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    due_date: datetime | None = datetime.now() + timedelta(days=30)
    total_ht: float | None = None
    total_ttc: float | None = None
    total_tva: float | None = None
    payment_status: PaymentStatus | None = PaymentStatus.PENDING
    # payment_details: dict | None = None
    payment_date: datetime | None = None
    public_url: str | None = None

    def generate_public_url(self):
        return hashlib.sha512(f"{self.number}".encode("utf-8")).hexdigest()


class Invoice(InvoiceBase, table=True):
    id: int = Field(default=None, primary_key=True)
    lots: list["Lot"] = Relationship(back_populates="invoice")
    orga_uuid: UUID = Field(default=None, foreign_key="organisation.uuid")
    organisation: "Organisation" = Relationship(
        back_populates="invoices",
        sa_relationship_kwargs={
            "foreign_keys": "Invoice.orga_uuid",
            "lazy": "selectin",
        },
    )
    sale_id: int | None = Field(default=None, foreign_key="sale.id")
    sale: "Sale" = Relationship(back_populates="invoices")
    client: "Client" = Relationship(back_populates="invoices")


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceRead(InvoiceBase):
    id: int
    lots: list["LotRead"]
    public_url: str | None = None


class InvoiceUpdate(SQLModel):
    updated_at: datetime = Field(default_factory=datetime.now)
    total_ht: float | None = None
    total_ttc: float | None = None
    total_tva: float | None = None
    payment_status: PaymentStatus | None = None
    # payment_details: dict | None = None
    payment_date: datetime | None = None
