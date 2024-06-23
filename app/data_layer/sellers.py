from sqlmodel import Session, select
from app.models.sellers import Seller, SellerCreate, SellerRead, SellerUpdate
from app.core.exceptions import DatabaseOperationError, SellerNotFoundError

def create_seller(session: Session, seller_create: SellerCreate) -> SellerRead:
    """
    Create a new seller in the database.

    Args:
        session (Session): The database session.
        seller_create (SellerCreate): The seller data to create.

    Returns:
        SellerRead: The created seller data.

    Raises:
        DatabaseOperationError: If an error occurs during seller creation.
    """
    try:
        seller = Seller.model_validate(seller_create)
        session.add(seller)
        session.commit()
        session.refresh(seller)
        return SellerRead.model_validate(seller)
    except Exception as e:
        session.rollback()
        raise DatabaseOperationError(f"Failed to create seller: {str(e)}")

def get_seller_by_id(session: Session, seller_id: int) -> SellerRead:
    """
    Retrieve a seller by its ID.

    Args:
        session (Session): The database session.
        seller_id (int): The ID of the seller to retrieve.

    Returns:
        SellerRead: The retrieved seller data.

    Raises:
        SellerNotFoundError: If the seller is not found.
    """
    seller = session.get(Seller, seller_id)
    if not seller:
        raise SellerNotFoundError(f"Seller with id {seller_id} not found")
    return SellerRead.model_validate(seller)

def update_seller(session: Session, seller_id: int, seller_update: SellerUpdate) -> SellerRead:
    """
    Update an existing seller in the database.

    Args:
        session (Session): The database session.
        seller_id (int): The ID of the seller to update.
        seller_update (SellerUpdate): The updated seller data.

    Returns:
        SellerRead: The updated seller data.

    Raises:
        SellerNotFoundError: If the seller is not found.
        DatabaseOperationError: If an error occurs during the update operation.
    """
    seller = session.get(Seller, seller_id)
    if not seller:
        raise SellerNotFoundError(f"Seller with id {seller_id} not found")

    try:
        seller_data = seller_update.model_dump(exclude_unset=True)
        for key, value in seller_data.items():
            setattr(seller, key, value)
        session.add(seller)
        session.commit()
        session.refresh(seller)
        return SellerRead.model_validate(seller)
    except Exception as e:
        session.rollback()
        raise DatabaseOperationError(f"Failed to update seller: {str(e)}")

def delete_seller(session: Session, seller_id: int) -> SellerRead:
    """
    Delete a seller from the database.

    Args:
        session (Session): The database session.
        seller_id (int): The ID of the seller to delete.

    Returns:
        SellerRead: The deleted seller data.

    Raises:
        SellerNotFoundError: If the seller is not found.
        DatabaseOperationError: If an error occurs during the delete operation.
    """
    seller = session.get(Seller, seller_id)
    if not seller:
        raise SellerNotFoundError(f"Seller with id {seller_id} not found")

    try:
        deleted_seller = SellerRead.model_validate(seller)
        session.delete(seller)
        session.commit()
        return deleted_seller
    except Exception as e:
        session.rollback()
        raise DatabaseOperationError(f"Failed to delete seller: {str(e)}")

def get_sellers(session: Session, skip: int = 0, limit: int = 100) -> list[SellerRead]:
    """
    Retrieve a list of sellers.

    Args:
        session (Session): The database session.
        skip (int): The number of sellers to skip (for pagination).
        limit (int): The maximum number of sellers to return.

    Returns:
        list[SellerRead]: A list of retrieved sellers.

    Raises:
        DatabaseOperationError: If an error occurs during the retrieval operation.
    """
    try:
        statement = select(Seller).offset(skip).limit(limit)
        sellers = session.exec(statement).all()
        return [SellerRead.model_validate(seller) for seller in sellers]
    except Exception as e:
        raise DatabaseOperationError(f"Failed to retrieve sellers: {str(e)}")

def get_sellers_by_organisation(session: Session, organisation_id: int, skip: int = 0, limit: int = 100) -> list[SellerRead]:
    """
    Retrieve a list of sellers for a specific organisation.

    Args:
        session (Session): The database session.
        organisation_id (int): The ID of the organisation.
        skip (int): The number of sellers to skip (for pagination).
        limit (int): The maximum number of sellers to return.

    Returns:
        list[SellerRead]: A list of retrieved sellers for the specified organisation.

    Raises:
        DatabaseOperationError: If an error occurs during the retrieval operation.
    """
    try:
        statement = (
            select(Seller)
            .where(Seller.organisation_id == organisation_id)
            .offset(skip)
            .limit(limit)
        )
        sellers = session.exec(statement).all()
        return [SellerRead.model_validate(seller) for seller in sellers]
    except Exception as e:
        raise DatabaseOperationError(f"Failed to retrieve sellers for organisation: {str(e)}")