from sqlmodel import select
from app.models.sales import Sale, SaleCreate, SaleRead, SaleUpdate
from app.core.exceptions import DatabaseOperationError, SaleNotFoundError
from app.core.database import get_db_session

def create_sale(sale_create: SaleCreate) -> SaleRead:
    """
    Create a new sale in the database.

    Args:
        
        sale_create (SaleCreate): The sale data to create.

    Returns:
        SaleRead: The created sale data.

    Raises:
        HTTPException: If an error occurs during sale creation or if the user is not authorized.
    """
    with get_db_session() as session:
        try:
            sale = Sale.model_validate(sale_create)
            session.add(sale)
            session.commit()
            session.refresh(sale)
            return SaleRead.model_validate(sale)
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(f"Failed to create sale: {str(e)}")


def get_sale_by_id(sale_id: int) -> SaleRead:
    """
    Retrieve a sale by its ID.

    Args:
        
        sale_id (int): The ID of the sale to retrieve.

    Returns:
        SaleRead: The retrieved sale data.

    Raises:
        HTTPException: If the sale is not found or if the user is not authorized.
    """
    with get_db_session() as session:
        sale = session.get(Sale, sale_id)
        if not sale:
            raise SaleNotFoundError(f"Sale with id {sale_id} not found")
        return SaleRead.model_validate(sale)


def update_sale(sale_id: int, sale_update: SaleUpdate) -> SaleRead:
    """
    Update an existing sale in the database.

    Args:
        
        sale_id (int): The ID of the sale to update.
        sale_update (SaleUpdate): The updated sale data.

    Returns:
        SaleRead: The updated sale data.

    Raises:
        HTTPException: If the sale is not found or if the user is not authorized.
    """
    with get_db_session() as session:
        sale = session.get(Sale, sale_id)
        if not sale:
            raise SaleNotFoundError(f"Sale with id {sale_id} not found")

        try:
            sale_data = sale_update.model_dump(exclude_unset=True)
            for key, value in sale_data.items():
                setattr(sale, key, value)
            session.add(sale)
            session.commit()
            session.refresh(sale)
            return SaleRead.model_validate(sale)
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(f"Failed to update sale: {str(e)}")


def delete_sale(sale_id: int) -> SaleRead:
    """
    Delete a sale from the database.

    Args:
        
        sale_id (int): The ID of the sale to delete.

    Returns:
        SaleRead: The deleted sale data.

    Raises:
        HTTPException: If the sale is not found, has associated lots, or if the user is not authorized.
    """
    with get_db_session() as session:
        sale = session.get(Sale, sale_id)
        if not sale:
            raise SaleNotFoundError(f"Sale with id {sale_id} not found")

        try:
            deleted_sale = SaleRead.model_validate(sale)
            session.delete(sale)
            session.commit()
            return deleted_sale
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(f"Failed to delete sale: {str(e)}")


def get_sales(skip: int = 0, limit: int = 100) -> list[SaleRead]:
    """
    Retrieve a list of sales.
    """
    with get_db_session() as session:
        try:
            statement = select(Sale).offset(skip).limit(limit)
            sales = session.exec(statement).all()
            return [SaleRead.model_validate(sale) for sale in sales]
        except Exception as e:
            raise DatabaseOperationError(f"Failed to retrieve sales: {str(e)}")


def get_sales_by_organisation(
    organisation_id: int, skip: int = 0, limit: int = 100
) -> list[SaleRead]:
    """
    Retrieve a list of sales for a specific organisation.
    """
    with get_db_session() as session:
        try:
            statement = (
                select(Sale)
                .where(Sale.organisation_id == organisation_id)
                .offset(skip)
                .limit(limit)
            )
            sales = session.exec(statement).all()
            return [SaleRead.model_validate(sale) for sale in sales]
        except Exception as e:
            raise DatabaseOperationError(
                f"Failed to retrieve sales for organisation: {str(e)}"
            )
