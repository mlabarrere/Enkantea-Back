from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.models.clients import Client, ClientCreate, ClientRead, ClientUpdate
from app.models.lots import Lot
from app.data_layer.utils import is_user_authorized_for_organisation


def create_client(
    session: Session, user_id: int, client_create: ClientCreate
) -> ClientRead:
    """
    Create a new client in the database.

    Args:
        session (Session): The database session.
        user_id (int): The ID of the user creating the client.
        client_create (ClientCreate): The client data to create.

    Returns:
        ClientRead: The created client data.

    Raises:
        HTTPException: If an error occurs during client creation or if the user is not authorized.
    """
    if not is_user_authorized_for_organisation(
        session, user_id, client_create.organisation_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized to create clients for this organisation.",
        )

    try:
        client = Client.model_validate(client_create)
        session.add(client)
        session.commit()
        session.refresh(client)
        return client
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the client: {str(e)}",
        )


def get_client_by_id(session: Session, user_id: int, client_id: int) -> ClientRead:
    """
    Retrieve a client by its ID.

    Args:
        session (Session): The database session.
        user_id (int): The ID of the user retrieving the client.
        client_id (int): The ID of the client to retrieve.

    Returns:
        ClientRead: The retrieved client data.

    Raises:
        HTTPException: If the client is not found or if the user is not authorized.
    """
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
        )

    if not is_user_authorized_for_organisation(
        session, user_id, client.organisation_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized to access this client.",
        )

    return client


def update_client(
    session: Session, user_id: int, client_id: int, client_update: dict
) -> ClientRead:
    """
    Update an existing client in the database.
    Args:
        session (Session): The database session.
        user_id (int): The ID of the user updating the client.
        client_id (int): The ID of the client to update.
        client_update (ClientUpdate): The updated client data.
    Returns:
        ClientRead: The updated client data.
    Raises:
        HTTPException: If the client is not found or if the user is not authorized.
    """
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
        )
    if not is_user_authorized_for_organisation(
        session, user_id, client.organisation_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized to update this client.",
        )
    try:
        #update_data = client_update.dict(exclude_unset=True)
        for key, value in client_update.items():
            setattr(client, key, value)
        session.commit()
        session.refresh(client)
        return client
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the client: {str(e)}",
        )

def delete_client(session: Session, user_id: int, client_id: int) -> ClientRead:
    """
    Delete a client from the database.

    Args:
        session (Session): The database session.
        user_id (int): The ID of the user deleting the client.
        client_id (int): The ID of the client to delete.

    Returns:
        ClientRead: The deleted client data.

    Raises:
        HTTPException: If the client is not found, has associated lots, or if the user is not authorized.
    """
    try:
        client = session.get(Client, client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
            )

        if not is_user_authorized_for_organisation(
            session, user_id, client.organisation_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not authorized to delete this client.",
            )

        if (
            session.exec(select(Lot).where(Lot.seller_id == client_id)).first()
            or session.exec(select(Lot).where(Lot.buyer_id == client_id)).first()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete client with associated lots.",
            )

        session.delete(client)
        session.commit()
        return client
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the client: {str(e)}",
        )
