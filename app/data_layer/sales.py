from sqlmodel import Session, select
from app.models.sales import Sale, SaleCreate, SaleRead, SaleUpdate
from app.core.exceptions import DatabaseOperationError, SaleNotFoundError


def create_sale(session: Session, sale_create: SaleCreate) -> SaleRead:
    """
    Create a new sale in the database.

    Args:
        session (Session): The database session.
        sale_create (SaleCreate): The sale data to create.

    Returns:
        SaleRead: The created sale data.

    Raises:
        DatabaseOperationError: If an error occurs during sale creation.
    """
    try:
        sale = Sale.model_validate(sale_create)
        session.add(sale)
        session.commit()
        session.refresh(sale)
        return SaleRead.model_validate(sale)
    except Exception as e:
        session.rollback()
        raise DatabaseOperationError(f"Failed to create sale: {str(e)}")


def get_sale_by_id(session: Session, sale_id: int) -> SaleRead:
    """
    Retrieve a sale by its ID.

    Args:
        session (Session): The database session.
        sale_id (int): The ID of the sale to retrieve.

    Returns:
        SaleRead: The retrieved sale data.

    Raises:
        SaleNotFoundError: If the sale is not found.
    """
    sale = session.get(Sale, sale_id)
    if not sale:
        raise SaleNotFoundError(f"Sale with id {sale_id} not found")
    return SaleRead.model_validate(sale)


def update_sale(session: Session, sale_id: int, sale_update: SaleUpdate) -> SaleRead:
    """
    Update an existing sale in the database.

    Args:
        session (Session): The database session.
        sale_id (int): The ID of the sale to update.
        sale_update (SaleUpdate): The updated sale data.

    Returns:
        SaleRead: The updated sale data.

    Raises:
        SaleNotFoundError: If the sale is not found.
        DatabaseOperationError: If an error occurs during the update operation.
    """
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


def delete_sale(session: Session, sale_id: int) -> SaleRead:
    """
    Delete a sale from the database.

    Args:
        session (Session): The database session.
        sale_id (int): The ID of the sale to delete.

    Returns:
        SaleRead: The deleted sale data.

    Raises:
        SaleNotFoundError: If the sale is not found.
        DatabaseOperationError: If an error occurs during the delete operation.
    """
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


def get_sales(session: Session, skip: int = 0, limit: int = 100) -> list[SaleRead]:
    """
    Retrieve a list of sales.
    """
    try:
        statement = select(Sale).offset(skip).limit(limit)
        sales = session.exec(statement).all()
        return [SaleRead.model_validate(sale) for sale in sales]
    except Exception as e:
        raise DatabaseOperationError(f"Failed to retrieve sales: {str(e)}")


def get_sales_by_organisation(
    session: Session, organisation_id: int, skip: int = 0, limit: int = 100
) -> list[SaleRead]:
    """
    Retrieve a list of sales for a specific organisation.
    """
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
