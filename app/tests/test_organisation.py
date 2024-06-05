import pytest
from sqlmodel import Session, create_engine, SQLModel
from app.crud.organisations import (
    create_organisation,
    update_organisation,
    get_organisation_by_id,
    get_organisation_by_name,
    delete_organisation,
)
from fastapi import HTTPException
from app.models.organisations import OrganisationCreate, OrganisationUpdate, CompanyType
from fastapi.testclient import TestClient
from app.main import app

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=False)


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture():
    return TestClient(app)


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


def test_create_organisation(session: Session) -> None:
    organisation_in = OrganisationCreate(**orga_data_tests)
    organisation = create_organisation(
        session=session, organisation_create=organisation_in
    )
    assert organisation.company_name == organisation_in.company_name
    assert organisation.siren_number == organisation_in.siren_number


def test_update_organisation(session: Session) -> None:
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

