# from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4
from app.lots.models import Lot
from app.organisations.models_organisations import Organisation
from app.sellers.models import Seller

# if TYPE_CHECKING:


class InventoryType(str, Enum):
    SUCCESSION = "succession"
    PARTITION = "partition"
    GUARDIANSHIP = "guardianship"
    DONATION = "donation"
    CREDIT = "credit"
    JUDICIAL = "judicial"
    PATRIMONIAL = "patrimonial"
    AUCTION = "auction"
    COLLECTIVE_PROCEDURE = "collective_procedure"


class InventoryBase(SQLModel):
    title: str
    description: str | None = None
    inventory_type: InventoryType
    inventory_date: datetime
    location: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Inventory(InventoryBase, table=True):
    uuid: UUID = Field(default_factory=uuid4, primary_key=True, index=True, unique=True)
    orga_uuid: UUID = Field(foreign_key="organisation.uuid")
    organisation: Organisation = Relationship(back_populates="inventories")
    lots: list["Lot"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "foreign(Lot.id) == Inventory.uuid",
            "lazy": "selectin",
        }
    )
    seller_id: int | None = Field(default=None, foreign_key="seller.id")


class InventoryCreate(InventoryBase):
    orga_uuid: UUID


class InventoryRead(InventoryBase):
    id: int
    uuid: UUID
    orga_uuid: UUID
    public_url: str | None = None
    lots: list[Lot] = []
    seller_id: int | None = None
    seller: Seller


class InventoryUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    inventory_type: InventoryType | None = None
    inventory_date: datetime | None = None
    location: str | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
