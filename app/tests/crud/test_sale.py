import pytest
from sqlmodel import Session, create_engine, SQLModel, select
from fastapi import HTTPException, status
from datetime import datetime, timezone
from app.models.users import User, UserCreate, UserRole, UserOrganisationLink
from app.models.clients import Client, ClientCreate
from app.models.lots import Lot, LotCreate, LotUpdate, LotRead
from app.models.organisations import Organisation, OrganisationCreate
from app.models.sales import Sale, SaleCreate, SaleUpdate
from app.crud.users import create_user, add_user_to_organisation
from app.crud.clients import create_client
from app.crud.lots import create_lot
from app.crud.sales import create_sale, get_sale_by_id, update_sale, delete_sale
from app.crud.organisations import create_organisation

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=False)

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

def test_create_sale(session: Session) -> None:
    """
    Test the creation of a sale.
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

    sale_data = {
        "number": 1,
        "title": "Test Sale",
        "description": "Test Description",
        "start_datetime": datetime.now(timezone.utc),
        "end_datetime": datetime.now(timezone.utc),
        "organisation_id": organisation.id
    }
    sale_create = SaleCreate(**sale_data)
    sale = create_sale(session=session, user_id=user.id, sale_create=sale_create)
    
    # Vérification de la création de la vente
    assert sale.title == sale_data["title"]
    assert sale.description == sale_data["description"]
    assert sale.organisation_id == organisation.id

def test_get_sale_by_id(session: Session) -> None:
    """
    Test retrieving a sale by its ID.
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

    sale_data = {
        "number": 1,
        "title": "Test Sale",
        "description": "Test Description",
        "start_datetime": datetime.now(timezone.utc),
        "end_datetime": datetime.now(timezone.utc),
        "organisation_id": organisation.id
    }
    sale_create = SaleCreate(**sale_data)
    created_sale = create_sale(session=session, user_id=user.id, sale_create=sale_create)

    fetched_sale = get_sale_by_id(session=session, user_id=user.id, sale_id=created_sale.id)
    
    # Vérification de la récupération de la vente
    assert fetched_sale.id == created_sale.id
    assert fetched_sale.title == created_sale.title

def test_update_sale(session: Session) -> None:
    """
    Test updating a sale's details.
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

    sale_data = {
        "number": 1,
        "title": "Test Sale",
        "description": "Test Description",
        "start_datetime": datetime.now(timezone.utc),
        "end_datetime": datetime.now(timezone.utc),
        "organisation_id": organisation.id
    }
    sale_create = SaleCreate(**sale_data)
    created_sale = create_sale(session=session, user_id=user.id, sale_create=sale_create)

    update_data = {"title": "Updated Sale", "description": "Updated Description"}
    sale_update = SaleUpdate(**update_data)
    updated_sale = update_sale(session=session, user_id=user.id, sale_id=created_sale.id, sale_update=sale_update)
    
    # Vérification de la mise à jour de la vente
    assert updated_sale.title == update_data["title"]
    assert updated_sale.description == update_data["description"]

def test_delete_sale(session: Session) -> None:
    """
    Test deleting a sale.
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

    sale_data = {
        "number": 1,
        "title": "Test Sale",
        "description": "Test Description",
        "start_datetime": datetime.now(timezone.utc),
        "end_datetime": datetime.now(timezone.utc),
        "organisation_id": organisation.id
    }
    sale_create = SaleCreate(**sale_data)
    created_sale = create_sale(session=session, user_id=user.id, sale_create=sale_create)

    deleted_sale = delete_sale(session=session, user_id=user.id, sale_id=created_sale.id)
    
    # Vérification de la suppression de la vente
    assert deleted_sale.id == created_sale.id
    with pytest.raises(HTTPException) as excinfo:
        get_sale_by_id(session=session, user_id=user.id, sale_id=created_sale.id)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
