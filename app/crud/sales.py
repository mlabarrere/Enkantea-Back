from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.models.sales import Sale, SaleCreate, SaleRead, SaleUpdate
from app.models.lots import Lot, LotRead, LotCreate, LotUpdate
from app.crud.utils import is_user_authorized_for_organisation
from fastapi import HTTPException, status
from datetime import datetime
from app.models.users import User, UserCreate, UserRole, UserOrganisationLink
from app.models.clients import Client, ClientCreate, ClientUpdate
from app.models.lots import Lot
from app.models.organisations import Organisation, OrganisationCreate
from app.crud.users import create_user, add_user_to_organisation
from app.crud.clients import create_client, get_client_by_id, update_client, delete_client
from app.crud.organisations import create_organisation
from app.crud.lots import create_lot



def create_sale(session: Session, user_id: int, sale_create: SaleCreate) -> SaleRead:
    """
    Create a new sale in the database.

    Args:
        session (Session): The database session.
        user_id (int): The ID of the user creating the sale.
        sale_create (SaleCreate): The sale data to create.

    Returns:
        SaleRead: The created sale data.

    Raises:
        HTTPException: If an error occurs during sale creation or if the user is not authorized.
    """
    if not is_user_authorized_for_organisation(session, user_id, sale_create.organisation_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized to create sales for this organisation."
        )

    try:
        sale = Sale.model_validate(sale_create)
        session.add(sale)
        session.commit()
        session.refresh(sale)
        return SaleRead.model_validate(sale)
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the sale: {str(e)}"
        )

def get_sale_by_id(session: Session, user_id: int, sale_id: int) -> SaleRead:
    """
    Retrieve a sale by its ID.

    Args:
        session (Session): The database session.
        user_id (int): The ID of the user retrieving the sale.
        sale_id (int): The ID of the sale to retrieve.

    Returns:
        SaleRead: The retrieved sale data.

    Raises:
        HTTPException: If the sale is not found or if the user is not authorized.
    """
    sale = session.get(Sale, sale_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found"
        )

    if not is_user_authorized_for_organisation(session, user_id, sale.organisation_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized to access this sale."
        )

    return SaleRead.model_validate(sale)

def update_sale(session: Session, user_id: int, sale_id: int, sale_update: SaleUpdate) -> SaleRead:
    """
    Update an existing sale in the database.

    Args:
        session (Session): The database session.
        user_id (int): The ID of the user updating the sale.
        sale_id (int): The ID of the sale to update.
        sale_update (SaleUpdate): The updated sale data.

    Returns:
        SaleRead: The updated sale data.

    Raises:
        HTTPException: If the sale is not found or if the user is not authorized.
    """
    try:
        sale = session.get(Sale, sale_id)
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sale not found"
            )

        if not is_user_authorized_for_organisation(session, user_id, sale.organisation_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not authorized to update this sale."
            )

        for key, value in sale_update.model_dump(exclude_unset=True).items():
            setattr(sale, key, value)
        
        session.add(sale)
        session.commit()
        session.refresh(sale)
        return SaleRead.model_validate(sale)
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the sale: {str(e)}"
        )

def delete_sale(session: Session, user_id: int, sale_id: int) -> SaleRead:
    """
    Delete a sale from the database.

    Args:
        session (Session): The database session.
        user_id (int): The ID of the user deleting the sale.
        sale_id (int): The ID of the sale to delete.

    Returns:
        SaleRead: The deleted sale data.

    Raises:
        HTTPException: If the sale is not found, has associated lots, or if the user is not authorized.
    """
    try:
        sale = session.get(Sale, sale_id)
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sale not found"
            )

        if not is_user_authorized_for_organisation(session, user_id, sale.organisation_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not authorized to delete this sale."
            )

        if session.exec(select(Lot).where(Lot.sale_id == sale_id)).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete sale with associated lots."
            )

        session.delete(sale)
        session.commit()
        return SaleRead.model_validate(sale)
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the sale: {str(e)}"
        )
