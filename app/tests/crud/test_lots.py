import pytest
from sqlmodel import Session, create_engine, SQLModel, select
from fastapi import HTTPException, status
from datetime import datetime
from app.models.users import User, UserCreate, UserRole, UserOrganisationLink
from app.models.clients import Client, ClientCreate
from app.models.lots import Lot, LotCreate, LotUpdate
from app.models.organisations import Organisation, OrganisationCreate
from app.crud.users import create_user, add_user_to_organisation
from app.crud.clients import create_client
from app.crud.lots import create_lot, get_lot_by_id, update_lot, delete_lot
from app.crud.organisations import create_organisation

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=False)

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

def test_create_user_with_organisation(session: Session) -> None:
    user_data = {
        "email": "user@example.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe"
    }
    user_create = UserCreate(**user_data)
    user = create_user(session=session, user_create=user_create)
    
    # Vérification de la création de l'utilisateur
    assert user.email == user_data["email"]
    assert user.first_name == user_data["first_name"]
    assert user.last_name == user_data["last_name"]

    # Vérification de la création de l'organisation via la relation utilisateur
    assert user.organisation is not None
    organisation = user.organisation
    organisation_name = f"{user_data['first_name']} {user_data['last_name']}"
    assert organisation.company_name == organisation_name

    # Vérification du lien entre l'utilisateur et l'organisation
    user_org_link = session.exec(
        select(UserOrganisationLink).where(
            UserOrganisationLink.user_id == user.id,
            UserOrganisationLink.organisation_id == organisation.id
        )
    ).first()
    assert user_org_link is not None
    assert user_org_link.role == UserRole.OWNER

def test_create_lot_with_organisation(session: Session) -> None:
    user_data = {
        "email": "user@example.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe"
    }
    user_create = UserCreate(**user_data)
    user = create_user(session=session, user_create=user_create)

    # Accès à l'organisation via l'utilisateur
    organisation = user.organisation
    
    client_data = {"first_name": "Client", "last_name": "Test", "organisation_id": organisation.id}
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
    lot = create_lot(session=session, user_id=user.id, lot_create=lot_create)
    
    # Vérification de la création du lot
    assert lot.name == lot_data["name"]
    assert lot.description == lot_data["description"]
    assert lot.organisation_id == organisation.id

def test_create_lot_in_different_organisations(session: Session) -> None:
    # Création de l'utilisateur et de la première organisation
    user_data = {
        "email": "user@example.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe"
    }
    user_create = UserCreate(**user_data)
    user = create_user(session=session, user_create=user_create)

    # Accès à la première organisation via l'utilisateur
    organisation1 = user.organisation
    
    # Création de la deuxième organisation
    organisation_data = {"company_name": "Second Organisation"}
    organisation_create = OrganisationCreate(**organisation_data)
    organisation2 = create_organisation(session=session, organisation_create=organisation_create)
    add_user_to_organisation(session=session, user_id=user.id, organisation_id=organisation2.id, role=UserRole.ADMIN)

    # Création d'un client dans la deuxième organisation
    client_data = {"first_name": "Client", "last_name": "Test", "organisation_id": organisation2.id}
    client_create = ClientCreate(**client_data)
    client = create_client(session=session, user_id=user.id, client_create=client_create)

    # Création d'un lot dans la deuxième organisation
    lot_data = {
        "name": "Test Lot",
        "description": "Test Description",
        "starting_bid": 100.0,
        "organisation_id": organisation2.id,
        "seller_id": client.id
    }
    lot_create = LotCreate(**lot_data)
    lot = create_lot(session=session, user_id=user.id, lot_create=lot_create)
    
    # Vérification de la création du lot dans la deuxième organisation
    assert lot.name == lot_data["name"]
    assert lot.description == lot_data["description"]
    assert lot.organisation_id == organisation2.id

def test_user_cannot_create_lot_in_unassigned_organisation(session: Session) -> None:
    # Création de l'utilisateur et de la première organisation
    user_data = {
        "email": "user@example.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe"
    }
    user_create = UserCreate(**user_data)
    user = create_user(session=session, user_create=user_create)

    # Accès à la première organisation via l'utilisateur
    organisation1 = user.organisation
    
    # Création de la deuxième organisation sans y ajouter l'utilisateur
    organisation_data = {"company_name": "Second Organisation"}
    organisation_create = OrganisationCreate(**organisation_data)
    organisation2 = create_organisation(session=session, organisation_create=organisation_create)

    # Création d'un client dans la deuxième organisation
    client_data = {"first_name": "Client", "last_name": "Test", "organisation_id": organisation2.id}
    client_create = ClientCreate(**client_data)
    client = create_client(session=session, user_id=user.id, client_create=client_create)

    # Tentative de création d'un lot dans la deuxième organisation
    lot_data = {
        "name": "Test Lot",
        "description": "Test Description",
        "starting_bid": 100.0,
        "organisation_id": organisation2.id,
        "seller_id": client.id
    }
    lot_create = LotCreate(**lot_data)
    with pytest.raises(HTTPException) as excinfo:
        create_lot(session=session, user_id=user.id, lot_create=lot_create)
    
    # Vérification de l'exception
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN

def test_update_lot(session: Session) -> None:
    """
    Test updating a lot's details.
    """
    user_data = {
        "email": "user@example.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe"
    }
    user_create = UserCreate(**user_data)
    user = create_user(session=session, user_create=user_create)

    # Accès à l'organisation via l'utilisateur
    organisation = user.organisation
    
    client_data = {"first_name": "Client", "last_name": "Test", "organisation_id": organisation.id}
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
    created_lot = create_lot(session=session, user_id=user.id, lot_create=lot_create)

    update_data = {"name": "Updated Lot", "description": "Updated Description"}
    lot_update = LotUpdate(**update_data)
    updated_lot = update_lot(session=session, user_id=user.id, lot_id=created_lot.id, lot_update=lot_update)
    
    # Vérification de la mise à jour du lot
    assert updated_lot.name == update_data["name"]
    assert updated_lot.description == update_data["description"]

def test_delete_lot(session: Session) -> None:
    """
    Test deleting a lot.
    """
    user_data = {
        "email": "user@example.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe"
    }
    user_create = UserCreate(**user_data)
    user = create_user(session=session, user_create=user_create)

    # Accès à l'organisation via l'utilisateur
    organisation = user.organisation
    
    client_data = {"first_name": "Client", "last_name": "Test", "organisation_id": organisation.id}
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
    created_lot = create_lot(session=session, user_id=user.id, lot_create=lot_create)

    deleted_lot = delete_lot(session=session, user_id=user.id, lot_id=created_lot.id)
    
    # Vérification de la suppression du lot
    assert deleted_lot.id == created_lot.id
    with pytest.raises(HTTPException) as excinfo:
        get_lot_by_id(session=session, user_id=user.id, lot_id=created_lot.id)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
