import pytest
from sqlmodel import Session, create_engine, SQLModel, select
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
from app.models.lots import Lot, LotCreate, LotUpdate

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=False)

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

def test_create_client(session: Session) -> None:
    """
    Test the creation of a client.
    """
    user_data = {
        "email": "user@example.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe"
    }
    user_create = UserCreate(**user_data)
    user = create_user(session=session, user_create=user_create)

    organisation = user.organisation

    client_data = {
        "first_name": "Client",
        "last_name": "Test",
        "organisation_id": organisation.id
    }
    client_create = ClientCreate(**client_data)
    client = create_client(session=session, user_id=user.id, client_create=client_create)
    
    # Vérification de la création du client
    assert client.first_name == client_data["first_name"]
    assert client.last_name == client_data["last_name"]
    assert client.organisation_id == organisation.id

def test_get_client_by_id(session: Session) -> None:
    """
    Test retrieving a client by its ID.
    """
    user_data = {
        "email": "user@example.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe"
    }
    user_create = UserCreate(**user_data)
    user = create_user(session=session, user_create=user_create)

    organisation = user.organisation

    client_data = {
        "first_name": "Client",
        "last_name": "Test",
        "organisation_id": organisation.id
    }
    client_create = ClientCreate(**client_data)
    created_client = create_client(session=session, user_id=user.id, client_create=client_create)

    fetched_client = get_client_by_id(session=session, user_id=user.id, client_id=created_client.id)
    
    # Vérification de la récupération du client
    assert fetched_client.id == created_client.id
    assert fetched_client.first_name == created_client.first_name

def test_update_client(session: Session) -> None:
    """
    Test updating a client's details.
    """
    user_data = {
        "email": "user@example.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe"
    }
    user_create = UserCreate(**user_data)
    user = create_user(session=session, user_create=user_create)

    organisation = user.organisation

    client_data = {
        "first_name": "Client",
        "last_name": "Test",
        "organisation_id": organisation.id
    }
    client_create = ClientCreate(**client_data)
    created_client = create_client(session=session, user_id=user.id, client_create=client_create)

    update_data = {"first_name": "UpdatedClient", "last_name": "UpdatedTest"}
    client_update = ClientUpdate(**update_data)
    updated_client = update_client(session=session, user_id=user.id, client_id=created_client.id, client_update=client_update)
    
    # Vérification de la mise à jour du client
    assert updated_client.first_name == update_data["first_name"]
    assert updated_client.last_name == update_data["last_name"]

def test_delete_client(session: Session) -> None:
    """
    Test deleting a client.
    """
    user_data = {
        "email": "user@example.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe"
    }
    user_create = UserCreate(**user_data)
    user = create_user(session=session, user_create=user_create)

    organisation = user.organisation

    client_data = {
        "first_name": "Client",
        "last_name": "Test",
        "organisation_id": organisation.id
    }
    client_create = ClientCreate(**client_data)
    created_client = create_client(session=session, user_id=user.id, client_create=client_create)

    deleted_client = delete_client(session=session, user_id=user.id, client_id=created_client.id)
    
    # Vérification de la suppression du client
    assert deleted_client.id == created_client.id
    with pytest.raises(HTTPException) as excinfo:
        get_client_by_id(session=session, user_id=user.id, client_id=created_client.id)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

def test_user_cannot_create_client_in_unassigned_organisation(session: Session) -> None:
    """
    Test that a user cannot create a client in an organisation they are not assigned to.
    """
    user_data = {
        "email": "user@example.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe"
    }
    user_create = UserCreate(**user_data)
    user = create_user(session=session, user_create=user_create)

    organisation1 = user.organisation
    
    # Création de la deuxième organisation sans y ajouter l'utilisateur
    organisation_data = {"company_name": "Second Organisation"}
    organisation_create = OrganisationCreate(**organisation_data)
    organisation2 = create_organisation(session=session, organisation_create=organisation_create)

    client_data = {
        "first_name": "Client",
        "last_name": "Test",
        "organisation_id": organisation2.id
    }
    client_create = ClientCreate(**client_data)
    with pytest.raises(HTTPException) as excinfo:
        create_client(session=session, user_id=user.id, client_create=client_create)
    
    # Vérification de l'exception
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN

def test_user_cannot_delete_client_with_associated_lots(session: Session) -> None:
    """
    Test that a user cannot delete a client with associated lots.
    """
    user_data = {
        "email": "user@example.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe"
    }
    user_create = UserCreate(**user_data)
    user = create_user(session=session, user_create=user_create)

    organisation = user.organisation

    client_data = {
        "first_name": "Client",
        "last_name": "Test",
        "organisation_id": organisation.id
    }
    client_create = ClientCreate(**client_data)
    client = create_client(session=session, user_id=user.id, client_create=client_create)

    lot_data = {
        "name": "Test Lot",
        "description": "Test Description",
        "starting_bid": 100.0,
        "organisation_id": organisation.id,
        "seller_id": client.id
    }
    lot_create = LotCreate(**lot_data)
    create_lot(session=session, user_id=user.id, lot_create=lot_create)

    with pytest.raises(HTTPException) as excinfo:
        delete_client(session=session, user_id=user.id, client_id=client.id)
    assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Cannot delete client with associated lots" in excinfo.value.detail
