import pytest
from uuid import UUID
from datetime import datetime, timezone
from app.inventories.models import InventoryCreate, InventoryUpdate, InventoryType
from app.lots.models import LotCreate
from app.inventories.CRUD import (
    get_lots_of_inventory,
    create_inventory,
    get_inventory_by_uuid,
    update_inventory,
    delete_inventory,
    get_inventories_of_organisation,
)
from app.lots.CRUD import create_lot, delete_lot


@pytest.fixture
def sample_inventory_create():
    return InventoryCreate(
        title="Test Inventory",
        description="A test inventory",
        inventory_type=InventoryType.AUCTION,
        inventory_date=datetime.now(timezone.utc),
        location="Test Location",
        orga_uuid=UUID("12345678-1234-5678-1234-567812345678"),
    )


@pytest.fixture
def sample_lot_create():
    return LotCreate(
        name="Test Lot",
        description="A test lot",
        orga_uuid=UUID("12345678-1234-5678-1234-567812345678"),
    )


async def test_inventory_crud_scenario():
    # Create an inventory
    inventory_create = sample_inventory_create()
    created_inventory = await create_inventory(inventory_create)
    assert created_inventory.title == "Test Inventory"
    assert created_inventory.uuid is not None

    # Add lots to the inventory
    lot_create1 = sample_lot_create()
    lot_create2 = sample_lot_create()

    created_lot1 = await create_lot(lot_create1)
    created_lot2 = await create_lot(lot_create2)

    # Verify lots are added
    inventory = await get_inventory_by_uuid(created_inventory.uuid)
    assert len(inventory.lots) == 2

    # Delete one lot
    await delete_lot(created_lot1.id)

    # Verify lot is deleted
    inventory = await get_inventory_by_uuid(created_inventory.uuid)
    assert len(inventory.lots) == 1

    # Add another lot
    lot_create3 = sample_lot_create()
    lot_create3.inventory_uuid = created_inventory.uuid
    created_lot3 = await create_lot(lot_create3)

    # Verify new lot is added
    inventory = await get_inventory_by_uuid(created_inventory.uuid)
    assert len(inventory.lots) == 2

    # Update inventory
    inventory_update = InventoryUpdate(title="Updated Test Inventory")
    updated_inventory = await update_inventory(created_inventory.uuid, inventory_update)
    assert updated_inventory.title == "Updated Test Inventory"

    # Delete inventory
    deleted_inventory = await delete_inventory(created_inventory.uuid)
    assert deleted_inventory.uuid == created_inventory.uuid

    # Verify inventory is deleted
    with pytest.raises(ValueError):
        await get_inventory_by_uuid(created_inventory.uuid)

    # Verify associated lots are also deleted
    lots = await get_lots_of_inventory(created_inventory.uuid)
    assert len(lots) == 0


async def test_get_inventories_of_organisation():
    orga_uuid = UUID("12345678-1234-5678-1234-567812345678")

    # Create multiple inventories
    for i in range(3):
        inventory_create = InventoryCreate(
            title=f"Test Inventory {i}",
            description=f"A test inventory {i}",
            inventory_type=InventoryType.AUCTION,
            inventory_date=datetime.now(timezone.utc),
            location=f"Test Location {i}",
            orga_uuid=orga_uuid,
        )
        await create_inventory(inventory_create)

    # Retrieve inventories
    inventories = await get_inventories_of_organisation(orga_uuid)
    assert len(inventories) == 3

    # Clean up
    for inventory in inventories:
        await delete_inventory(inventory.uuid)
