from uuid import UUID
from sqlmodel import select
from app.inventories.models import (
    Inventory,
    InventoryCreate,
    InventoryRead,
    InventoryUpdate,
)
from app.core.exceptions import DatabaseOperationError
from app.core.database import get_db_session
from app.lots.models import LotRead


async def create_inventory(inventory_create: InventoryCreate) -> InventoryRead:
    """
    Create a new inventory in the database.
    """
    with get_db_session() as session:
        try:
            inventory = Inventory.model_validate(inventory_create)
            session.add(inventory)
            session.commit()
            session.refresh(inventory)
            return InventoryRead.model_validate(inventory)
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(f"Failed to create inventory: {str(e)}")


async def get_inventory_by_uuid(inventory_uuid: UUID) -> InventoryRead:
    """
    Retrieve an inventory by its UUID.
    """
    with get_db_session() as session:
        inventory = session.get(Inventory, inventory_uuid)
        if not inventory:
            raise ValueError(f"Inventory with uuid {inventory_uuid} not found")
        return InventoryRead.model_validate(inventory)


async def update_inventory(
    inventory_uuid: UUID, inventory_update: InventoryUpdate
) -> InventoryRead:
    """
    Update an existing inventory in the database.
    """
    with get_db_session() as session:
        inventory = session.get(Inventory, inventory_uuid)
        if not inventory:
            raise ValueError(f"Inventory with uuid {inventory_uuid} not found")

        try:
            inventory_data = inventory_update.model_dump(exclude_unset=True)
            for key, value in inventory_data.items():
                setattr(inventory, key, value)
            session.add(inventory)
            session.commit()
            session.refresh(inventory)
            return InventoryRead.model_validate(inventory)
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(f"Failed to update inventory: {str(e)}")


async def delete_inventory(inventory_uuid: UUID) -> InventoryRead:
    """
    Delete an inventory from the database.
    """
    with get_db_session() as session:
        inventory = session.get(Inventory, inventory_uuid)
        if not inventory:
            raise ValueError(f"Inventory with uuid {inventory_uuid} not found")

        try:
            deleted_inventory = InventoryRead.model_validate(inventory)
            session.delete(inventory)
            session.commit()
            return deleted_inventory
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(f"Failed to delete inventory: {str(e)}")


async def get_inventories_of_organisation(
    orga_uuid: UUID, skip: int = 0, limit: int = 100
) -> list[InventoryRead]:
    """
    Retrieve inventories for a specific organisation.
    """
    with get_db_session() as session:
        try:
            statement = (
                select(Inventory)
                .where(Inventory.orga_uuid == orga_uuid)
                .offset(skip)
                .limit(limit)
            )
            results = session.exec(statement)
            return [InventoryRead.model_validate(inventory) for inventory in results]
        except Exception as e:
            raise DatabaseOperationError(
                f"Failed to get inventories of organisation: {str(e)}"
            )


async def get_lots_of_inventory(inventory_uuid: UUID) -> list[LotRead]:
    """
    Retrieve all lots of a specific inventory.
    """
    with get_db_session() as session:
        try:
            inventory = session.get(Inventory, inventory_uuid)
            if not inventory:
                raise ValueError(f"Inventory with uuid {inventory_uuid} not found")

            return [LotRead.model_validate(lot) for lot in inventory.lots]
        except Exception as e:
            raise DatabaseOperationError(f"Failed to get lots of inventory: {str(e)}")


async def search_and_filter_lots(
    inventory_uuid: UUID,
    search_term: str | None = None,
    min_estimate: float | None = None,
    max_estimate: float | None = None,
    category: str | None = None,
) -> list[LotRead]:
    """
    Search and filter lots within an inventory based on various criteria.
    """
    with get_db_session() as session:
        try:
            inventory = session.get(Inventory, inventory_uuid)
            if not inventory:
                raise ValueError(f"Inventory with uuid {inventory_uuid} not found")

            filtered_lots = inventory.lots

            if search_term:
                filtered_lots = [lot for lot in filtered_lots if search_term.lower() in lot.name.lower() or search_term.lower() in lot.description.lower()]  # type: ignore

            if min_estimate is not None:
                filtered_lots = [
                    lot
                    for lot in filtered_lots
                    if (
                        lot.low_estimate is not None
                        and lot.low_estimate >= min_estimate
                    )
                ]

            if max_estimate is not None:
                filtered_lots = [
                    lot
                    for lot in filtered_lots
                    if (
                        lot.high_estimate is not None
                        and lot.high_estimate <= max_estimate
                    )
                ]

            if category:
                filtered_lots = [
                    lot
                    for lot in filtered_lots
                    if (lot.category is not None and lot.category == category)
                ]

            return [LotRead.model_validate(lot) for lot in filtered_lots]
        except Exception as e:
            raise DatabaseOperationError(f"Failed to search and filter lots: {str(e)}")
