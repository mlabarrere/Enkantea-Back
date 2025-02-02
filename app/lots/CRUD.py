from uuid import UUID
from sqlmodel import select
from app.lots.models import Lot, LotCreate, LotRead, LotUpdate
from app.core.exceptions import DatabaseOperationError, LotNotFoundError
from app.core.database import get_db_session


async def create_lot(lot_create: LotCreate) -> LotRead:
    """
    Create a new lot in the database.

    Args:

        lot_create (LotCreate): The lot data to create.

    Returns:
        LotRead: The created lot data.

    Raises:
        HTTPException: If an error occurs during lot creation or if the user is not authorized.
    """
    with get_db_session() as session:
        try:
            lot = Lot.model_validate(lot_create)
            session.add(lot)
            session.commit()
            session.refresh(lot)
            return LotRead.model_validate(lot)
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(f"Failed to create lot: {str(e)}")


async def create_lots_batch(lots_create: list[LotCreate]) -> list[LotRead]:
    """
    Create multiple lots in the database in a single transaction.

    Args:

        lots_create (List[LotCreate]): A list of lot data to create.

    Returns:
        List[LotRead]: The list of created lot data.

    Raises:
        DatabaseOperationError: If an error occurs during lot creation.
    """
    with get_db_session() as session:
        try:
            lots = [Lot.model_validate(lot_create) for lot_create in lots_create]
            session.add_all(lots)
            session.commit()
            for lot in lots:
                session.refresh(lot)
            return [LotRead.model_validate(lot) for lot in lots]
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(f"Failed to create lots in batch: {str(e)}")


async def get_lot_by_id(lot_id: int) -> LotRead:
    """
    Retrieve a lot by its ID.

    Args:

        lot_id (int): The ID of the lot to retrieve.

    Returns:
        LotRead: The retrieved lot data.

    Raises:
        HTTPException: If the lot is not found or if the user is not authorized.
    """
    with get_db_session() as session:
        lot = session.get(Lot, lot_id)
        if not lot:
            raise LotNotFoundError(f"Lot with id {lot_id} not found")
        return LotRead.model_validate(lot)


async def update_lot(lot_update: LotUpdate) -> LotRead:
    """
    Update an existing lot in the database.

    Args:

        lot_id (int): The ID of the lot to update.
        lot_update (LotUpdate): The updated lot data.

    Returns:
        LotRead: The updated lot data.

    Raises:
        HTTPException: If the lot is not found or if the user is not authorized.
    """
    with get_db_session() as session:
        try:
            lot_data = lot_update.model_dump(exclude_unset=True)
            for key, value in lot_data.items():
                setattr(lot_update, key, value)
            session.add(lot_update)
            session.commit()
            session.refresh(lot_update)
            return LotRead.model_validate(lot_update)
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(f"Failed to update lot: {str(e)}")


async def delete_lot(lot_id: int) -> LotRead:
    """
    Delete a lot from the database.

    Args:

        lot_id (int): The ID of the lot to delete.

    Returns:
        LotRead: The deleted lot data.

    Raises:
        HTTPException: If the lot is not found or if the user is not authorized.
    """
    with get_db_session() as session:
        lot = session.get(Lot, lot_id)
        if not lot:
            raise LotNotFoundError(f"Lot with id {lot_id} not found")

        try:
            deleted_lot = LotRead.model_validate(lot)
            session.delete(lot)
            session.commit()
            return deleted_lot
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(f"Failed to delete lot: {str(e)}")


async def get_lots_of_organisation(
    orga_uuid: UUID, skip: int = 0, limit: int = 100
) -> list[LotRead]:
    with get_db_session() as session:
        try:
            statement = (
                select(Lot).where(Lot.orga_uuid == orga_uuid).offset(skip).limit(limit)
            )
            results = session.exec(statement)
            return [LotRead.model_validate(lot) for lot, _ in results]
        except Exception as e:
            raise DatabaseOperationError(
                f"Failed to get lots of organisation: {str(e)}"
            )
