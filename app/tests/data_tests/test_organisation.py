import pytest
from sqlmodel import Session, create_engine, SQLModel
from app.models.clients import Client
from app.models.sales import Sale
from app.models.lots import Lot
from app.models.invoices import Invoice
from app.models.organisations import (
    OrganisationCreate,
    OrganisationUpdate,
    CompanyType,
    Organisation,
)
from app.models.users import UserCreate, UserRole, UserOrganisationLink
from app.data_layer.users import create_user
from app.data_layer.organisations import (
    create_organisation,
    update_organisation,
    get_organisation_by_id,
    get_organisation_by_name,
    delete_organisation,
    add_member_to_organisation,
    remove_member_from_organisation,
)
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from app.main import app
from random import choices
from string import ascii_lowercase

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=False)


# Utility functions for random strings and emails
def random_lower_string() -> str:
    return "".join(choices(ascii_lowercase, k=5))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture():
    return TestClient(app)


def test_create_organisation(session: Session) -> None:
    orga_data_tests = {
        "company_name": "Test Company",
        "company_type": CompanyType.SA,
        "siren_number": 123456789,
        "ape_code": "6201Z",
        "share_capital": 10000.0,
        "start_date": "2020-01-01",
        "registration_date": "2020-01-01",
        "headquarter_siret_number": 12345678900010,
        "address": "123 Test St",
        "postal_code": "75000",
        "city": "Paris",
        "standard_seller_fees": 5,
        "standard_buyer_fees": 5,
        "expert_fees": 2,
    }
    organisation_in = OrganisationCreate(**orga_data_tests)
    organisation = create_organisation(
        session=session, organisation_create=organisation_in
    )
    assert organisation.company_name == organisation_in.company_name
    assert organisation.siren_number == organisation_in.siren_number


def test_update_organisation(session: Session) -> None:
    orga_data_tests = {
        "company_name": "Test Company",
        "company_type": CompanyType.SA,
        "siren_number": 123456789,
        "ape_code": "6201Z",
        "share_capital": 10000.0,
        "start_date": "2020-01-01",
        "registration_date": "2020-01-01",
        "headquarter_siret_number": 12345678900010,
        "address": "123 Test St",
        "postal_code": "75000",
        "city": "Paris",
        "standard_seller_fees": 5,
        "standard_buyer_fees": 5,
        "expert_fees": 2,
    }
    organisation_in = OrganisationCreate(**orga_data_tests)
    organisation = create_organisation(
        session=session, organisation_create=organisation_in
    )
    update_in = OrganisationUpdate(company_name="Updated Company")
    updated_organisation = update_organisation(
        session=session, db_organisation=organisation, organisation_in=update_in
    )
    assert updated_organisation.company_name == update_in.company_name


def test_get_organisation_by_id(session: Session) -> None:
    orga_data_tests = {
        "company_name": "Test Company",
        "company_type": CompanyType.SA,
        "siren_number": 123456789,
        "ape_code": "6201Z",
        "share_capital": 10000.0,
        "start_date": "2020-01-01",
        "registration_date": "2020-01-01",
        "headquarter_siret_number": 12345678900010,
        "address": "123 Test St",
        "postal_code": "75000",
        "city": "Paris",
        "standard_seller_fees": 5,
        "standard_buyer_fees": 5,
        "expert_fees": 2,
    }
    organisation_in = OrganisationCreate(**orga_data_tests)
    organisation = create_organisation(
        session=session, organisation_create=organisation_in
    )
    fetched_organisation = get_organisation_by_id(
        session=session, organisation_id=organisation.id
    )
    assert fetched_organisation
    assert fetched_organisation.id == organisation.id


def test_get_organisation_by_name(session: Session) -> None:
    orga_data_tests = {
        "company_name": "Test Company",
        "company_type": CompanyType.SA,
        "siren_number": 123456789,
        "ape_code": "6201Z",
        "share_capital": 10000.0,
        "start_date": "2020-01-01",
        "registration_date": "2020-01-01",
        "headquarter_siret_number": 12345678900010,
        "address": "123 Test St",
        "postal_code": "75000",
        "city": "Paris",
        "standard_seller_fees": 5,
        "standard_buyer_fees": 5,
        "expert_fees": 2,
    }
    organisation_in = OrganisationCreate(**orga_data_tests)
    organisation = create_organisation(
        session=session, organisation_create=organisation_in
    )
    fetched_organisation = get_organisation_by_name(
        session=session, company_name=organisation.company_name
    )
    assert fetched_organisation
    assert fetched_organisation.company_name == organisation.company_name


def test_delete_organisation(session: Session) -> None:
    organisation_in = OrganisationCreate(company_name="Deleted Company")
    organisation = create_organisation(
        session=session, organisation_create=organisation_in
    )
    deleted_organisation = delete_organisation(
        session=session, organisation_id=organisation.id
    )
    assert deleted_organisation
    assert deleted_organisation.id == organisation.id
    with pytest.raises(HTTPException) as excinfo:
        get_organisation_by_id(session=session, organisation_id=organisation.id) is None
        assert excinfo.value.status_code == 404


def test_add_member_to_organisation(session: Session) -> None:
    user_data_tests = {
        "last_name": "Pépito",
        "first_name": random_lower_string(),
        "password": random_lower_string(),
        "email": "pepito@gmail.com",
    }
    user_in = UserCreate(**user_data_tests)
    user = create_user(session=session, user_create=user_in)

    organisation_data = {"company_name": "Test Organisation"}
    organisation = Organisation(**organisation_data)
    session.add(organisation)
    session.commit()
    session.refresh(organisation)

    user_org_link = add_member_to_organisation(
        session=session,
        user_id=user.id,
        organisation_id=organisation.id,
        role=UserRole.USER,
    )
    assert user_org_link
    assert user_org_link.user_id == user.id
    assert user_org_link.organisation_id == organisation.id
    assert user_org_link.role == UserRole.USER


def test_remove_member_from_organisation(session: Session) -> None:
    user_data_tests = {
        "last_name": "Pépito",
        "first_name": random_lower_string(),
        "password": random_lower_string(),
        "email": "pepito@gmail.com",
    }
    user_in = UserCreate(**user_data_tests)
    user = create_user(session=session, user_create=user_in)

    organisation_data = {"company_name": "Test Organisation"}
    organisation = Organisation(**organisation_data)
    session.add(organisation)
    session.commit()
    session.refresh(organisation)

    user_org_link = add_member_to_organisation(
        session=session,
        user_id=user.id,
        organisation_id=organisation.id,
        role=UserRole.USER,
    )
    assert user_org_link

    remove_member_from_organisation(
        session=session, user_id=user.id, organisation_id=organisation.id
    )
    user_org_link = session.get(UserOrganisationLink, (user.id, organisation.id))
    assert not user_org_link

    # Test trying to remove owner
    owner_link = UserOrganisationLink(
        user_id=user.id, organisation_id=organisation.id, role=UserRole.OWNER
    )
    session.add(owner_link)
    session.commit()
    session.refresh(owner_link)

    with pytest.raises(HTTPException) as excinfo:
        remove_member_from_organisation(
            session=session, user_id=user.id, organisation_id=organisation.id
        )
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot remove the owner of the organisation" in excinfo.value.detail
