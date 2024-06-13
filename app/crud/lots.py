from sqlmodel import Session
from fastapi import HTTPException, status
from app.models.lots import Lot, LotCreate, LotRead, LotUpdate
from app.crud.utils import is_user_authorized_for_organisation


def create_lot(session: Session, user_id: int, lot_create: LotCreate) -> LotRead:
    """
    Create a new lot in the database.

    Args:
        session (Session): The database session.
        user_id (int): The ID of the user creating the lot.
        lot_create (LotCreate): The lot data to create.

    Returns:
        LotRead: The created lot data.

    Raises:
        HTTPException: If an error occurs during lot creation or if the user is not authorized.
    """
    if not is_user_authorized_for_organisation(
        session, user_id, lot_create.organisation_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized to create lots for this organisation.",
        )

    try:
        lot = Lot.model_validate(lot_create)
        session.add(lot)
        session.commit()
        session.refresh(lot)
        return lot
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the lot: {str(e)}",
        )


def get_lot_by_id(session: Session, user_id: int, lot_id: int) -> LotRead:
    """
    Retrieve a lot by its ID.

    Args:
        session (Session): The database session.
        user_id (int): The ID of the user retrieving the lot.
        lot_id (int): The ID of the lot to retrieve.

    Returns:
        LotRead: The retrieved lot data.

    Raises:
        HTTPException: If the lot is not found or if the user is not authorized.
    """
    lot = session.get(Lot, lot_id)
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lot not found"
        )

    if not is_user_authorized_for_organisation(session, user_id, lot.organisation_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized to access this lot.",
        )

    return lot


def update_lot(
    session: Session, user_id: int, lot_id: int, lot_update: LotUpdate
) -> LotRead:
    """
    Update an existing lot in the database.

    Args:
        session (Session): The database session.
        user_id (int): The ID of the user updating the lot.
        lot_id (int): The ID of the lot to update.
        lot_update (LotUpdate): The updated lot data.

    Returns:
        LotRead: The updated lot data.

    Raises:
        HTTPException: If the lot is not found or if the user is not authorized.
    """
    
    lot = session.get(Lot, lot_id)
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lot not found"
        )

    if not is_user_authorized_for_organisation(
        session, user_id, lot.organisation_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized to update this lot.",
        )
    try:
        for key, value in lot_update.model_dump(exclude_unset=True).items():
            setattr(lot, key, value)

        session.add(lot)
        session.commit()
        session.refresh(lot)
        return lot
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the lot: {str(e)}",
        )


def delete_lot(session: Session, user_id: int, lot_id: int) -> LotRead:
    """
    Delete a lot from the database.

    Args:
        session (Session): The database session.
        user_id (int): The ID of the user deleting the lot.
        lot_id (int): The ID of the lot to delete.

    Returns:
        LotRead: The deleted lot data.

    Raises:
        HTTPException: If the lot is not found or if the user is not authorized.
    """
    try:
        lot = session.get(Lot, lot_id)
        if not lot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Lot not found"
            )

        if not is_user_authorized_for_organisation(
            session, user_id, lot.organisation_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not authorized to delete this lot.",
            )

        session.delete(lot)
        session.commit()
        return lot
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the lot: {str(e)}",
        )
