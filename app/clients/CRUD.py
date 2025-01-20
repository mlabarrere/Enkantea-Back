from sqlmodel import select
from app.clients.models import Client, ClientCreate, ClientRead, ClientUpdate
from app.core.exceptions import DatabaseOperationError, ClientNotFoundError
from app.core.database import get_db_session
from uuid import UUID


def create_client(client_create: ClientCreate) -> ClientRead:
    """
    Create a new client in the database.

    Args:

        client_create (ClientCreate): The client data to create.

    Returns:
        ClientRead: The created client data.

    Raises:
        HTTPException: If an error occurs during client creation or if the user is not authorized.
    """
    with get_db_session() as session:
        try:
            client = Client.model_validate(client_create)
            session.add(client)
            session.commit()
            session.refresh(client)
            return ClientRead.model_validate(client)
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(f"Failed to create client: {str(e)}")


def get_client_by_uuid(client_id: int) -> ClientRead:
    """
    Retrieve a client by its ID.

    Args:

        client_id (int): The ID of the client to retrieve.

    Returns:
        ClientRead: The retrieved client data.

    Raises:
        HTTPException: If the client is not found or if the user is not authorized.
    """
    with get_db_session() as session:
        client = session.get(Client, client_id)
        if not client:
            raise ClientNotFoundError(f"Client with id {client_id} not found")
        return ClientRead.model_validate(client)


def update_client(client_id: int, client_update: ClientUpdate) -> ClientRead:
    """
    Update an existing client in the database.
    Args:

        client_id (int): The ID of the client to update.
        client_update (ClientUpdate): The updated client data.
    Returns:
        ClientRead: The updated client data.
    Raises:
        HTTPException: If the client is not found or if the user is not authorized.
    """
    with get_db_session() as session:
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


def delete_client(client_id: int) -> ClientRead:
    """
    Delete a client from the database.

    Args:

        client_id (UUID): The ID of the client to delete.

    Returns:
        ClientRead: The deleted client data.

    Raises:
        HTTPException: If the client is not found, has associated lots, or if the user is not authorized.
    """
    with get_db_session() as session:
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


def get_clients_by_organisation(
    orga_uuid: UUID, skip: int = 0, limit: int = 100
) -> list[ClientRead]:
    """
    Retrieve a list of clients for a specific organisation.

    Args:

        orga_uuid (UUID): The ID of the organisation.
        skip (int): The number of clients to skip (for pagination).
        limit (int): The maximum number of clients to return.

    Returns:
        list[ClientRead]: A list of retrieved clients for the specified organisation.

    Raises:
        DatabaseOperationError: If an error occurs during the retrieval operation.
    """
    with get_db_session() as session:
        try:
            statement = (
                select(Client)
                .where(Client.orga_uuid == orga_uuid)
                .offset(skip)
                .limit(limit)
            )
            clients = session.exec(statement).all()
            return [ClientRead.model_validate(client) for client in clients]
        except Exception as e:
            raise DatabaseOperationError(
                f"Failed to retrieve clients for organisation: {str(e)}"
            )
