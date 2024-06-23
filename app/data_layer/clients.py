from sqlmodel import Session, select
from app.models.clients import Client, ClientCreate, ClientRead, ClientUpdate
from app.core.exceptions import DatabaseOperationError, ClientNotFoundError


def create_client(session: Session, client_create: ClientCreate) -> ClientRead:
    """
    Create a new client in the database.

    Args:
        session (Session): The database session.
        client_create (ClientCreate): The client data to create.

    Returns:
        ClientRead: The created client data.

    Raises:
        DatabaseOperationError: If an error occurs during client creation.
    """
    try:
        client = Client.model_validate(client_create)
        session.add(client)
        session.commit()
        session.refresh(client)
        return ClientRead.model_validate(client)
    except Exception as e:
        session.rollback()
        raise DatabaseOperationError(f"Failed to create client: {str(e)}")


def get_client_by_id(session: Session, client_id: int) -> ClientRead:
    """
    Retrieve a client by its ID.

    Args:
        session (Session): The database session.
        client_id (int): The ID of the client to retrieve.

    Returns:
        ClientRead: The retrieved client data.

    Raises:
        ClientNotFoundError: If the client is not found.
    """
    client = session.get(Client, client_id)
    if not client:
        raise ClientNotFoundError(f"Client with id {client_id} not found")
    return ClientRead.model_validate(client)


def update_client(
    session: Session, client_id: int, client_update: ClientUpdate
) -> ClientRead:
    """
    Update an existing client in the database.

    Args:
        session (Session): The database session.
        client_id (int): The ID of the client to update.
        client_update (ClientUpdate): The updated client data.

    Returns:
        ClientRead: The updated client data.

    Raises:
        ClientNotFoundError: If the client is not found.
        DatabaseOperationError: If an error occurs during the update operation.
    """
    client = session.get(Client, client_id)
    if not client:
        raise ClientNotFoundError(f"Client with id {client_id} not found")

    try:
        client_data = client_update.model_dump(exclude_unset=True)
        for key, value in client_data.items():
            setattr(client, key, value)
        session.add(client)
        session.commit()
        session.refresh(client)
        return ClientRead.model_validate(client)
    except Exception as e:
        session.rollback()
        raise DatabaseOperationError(f"Failed to update client: {str(e)}")


def delete_client(session: Session, client_id: int) -> ClientRead:
    """
    Delete a client from the database.

    Args:
        session (Session): The database session.
        client_id (int): The ID of the client to delete.

    Returns:
        ClientRead: The deleted client data.

    Raises:
        ClientNotFoundError: If the client is not found.
        DatabaseOperationError: If an error occurs during the delete operation.
    """
    client = session.get(Client, client_id)
    if not client:
        raise ClientNotFoundError(f"Client with id {client_id} not found")

    try:
        deleted_client = ClientRead.model_validate(client)
        session.delete(client)
        session.commit()
        return deleted_client
    except Exception as e:
        session.rollback()
        raise DatabaseOperationError(f"Failed to delete client: {str(e)}")


def get_clients(session: Session, skip: int = 0, limit: int = 100) -> list[ClientRead]:
    """
    Retrieve a list of clients.

    Args:
        session (Session): The database session.
        skip (int): The number of clients to skip (for pagination).
        limit (int): The maximum number of clients to return.

    Returns:
        list[ClientRead]: A list of retrieved clients.

    Raises:
        DatabaseOperationError: If an error occurs during the retrieval operation.
    """
    try:
        statement = select(Client).offset(skip).limit(limit)
        clients = session.exec(statement).all()
        return [ClientRead.model_validate(client) for client in clients]
    except Exception as e:
        raise DatabaseOperationError(f"Failed to retrieve clients: {str(e)}")


def get_clients_by_organisation(
    session: Session, organisation_id: int, skip: int = 0, limit: int = 100
) -> list[ClientRead]:
    """
    Retrieve a list of clients for a specific organisation.

    Args:
        session (Session): The database session.
        organisation_id (int): The ID of the organisation.
        skip (int): The number of clients to skip (for pagination).
        limit (int): The maximum number of clients to return.

    Returns:
        list[ClientRead]: A list of retrieved clients for the specified organisation.

    Raises:
        DatabaseOperationError: If an error occurs during the retrieval operation.
    """
    try:
        statement = (
            select(Client)
            .where(Client.organisation_id == organisation_id)
            .offset(skip)
            .limit(limit)
        )
        clients = session.exec(statement).all()
        return [ClientRead.model_validate(client) for client in clients]
    except Exception as e:
        raise DatabaseOperationError(
            f"Failed to retrieve clients for organisation: {str(e)}"
        )
