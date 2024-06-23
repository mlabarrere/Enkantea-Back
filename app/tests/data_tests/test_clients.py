import pytest
from app.models.clients import ClientCreate, ClientRead, ClientUpdate
from app.core.exceptions import ClientNotFoundError
from app.data_layer.clients import (
    create_client,
    get_client_by_id,
    update_client,
    delete_client,
    get_clients,
    get_clients_by_organisation,
)
from app.data_layer.organisations import create_organisation
from app.models.organisations import OrganisationCreate


def test_create_client(db_session):
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(session=db_session, organisation_create=org_create)

    client_create = ClientCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        organisation_id=org.id,
    )
    result = create_client(session=db_session, client_create=client_create)

    assert isinstance(result, ClientRead)
    assert result.first_name == "John"
    assert result.last_name == "Doe"
    assert result.email == "john.doe@example.com"
    assert result.organisation_id == org.id


def test_get_client_by_id(db_session):
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(session=db_session, organisation_create=org_create)

    client_create = ClientCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        organisation_id=org.id,
    )
    created_client = create_client(session=db_session, client_create=client_create)

    result = get_client_by_id(session=db_session, client_id=created_client.id)

    assert isinstance(result, ClientRead)
    assert result.id == created_client.id
    assert result.first_name == "John"

    with pytest.raises(ClientNotFoundError):
        get_client_by_id(session=db_session, client_id=9999)


def test_update_client(db_session):
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(session=db_session, organisation_create=org_create)

    client_create = ClientCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        organisation_id=org.id,
    )
    created_client = create_client(session=db_session, client_create=client_create)

    update_data = ClientUpdate(first_name="Jane", email="jane.doe@example.com")
    result = update_client(
        session=db_session, client_id=created_client.id, client_update=update_data
    )

    assert isinstance(result, ClientRead)
    assert result.first_name == "Jane"
    assert result.email == "jane.doe@example.com"
    assert result.last_name == "Doe"  # Unchanged

    with pytest.raises(ClientNotFoundError):
        update_client(session=db_session, client_id=9999, client_update=update_data)


def test_delete_client(db_session):
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(session=db_session, organisation_create=org_create)

    client_create = ClientCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        organisation_id=org.id,
    )
    created_client = create_client(session=db_session, client_create=client_create)

    result = delete_client(session=db_session, client_id=created_client.id)

    assert isinstance(result, ClientRead)
    assert result.first_name == "John"

    with pytest.raises(ClientNotFoundError):
        get_client_by_id(session=db_session, client_id=created_client.id)

    with pytest.raises(ClientNotFoundError):
        delete_client(session=db_session, client_id=created_client.id)


def test_get_clients(db_session):
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(session=db_session, organisation_create=org_create)

    for i in range(5):
        client_create = ClientCreate(
            first_name=f"John{i}",
            last_name=f"Doe{i}",
            email=f"john{i}.doe@example.com",
            organisation_id=org.id,
        )
        create_client(session=db_session, client_create=client_create)

    results = get_clients(session=db_session, skip=0, limit=10)

    assert len(results) == 5
    assert all(isinstance(result, ClientRead) for result in results)


def test_get_clients_by_organisation(db_session):
    org_create1 = OrganisationCreate(name="Test Organisation 1")
    org1 = create_organisation(session=db_session, organisation_create=org_create1)

    org_create2 = OrganisationCreate(name="Test Organisation 2")
    org2 = create_organisation(session=db_session, organisation_create=org_create2)

    for i in range(3):
        client_create = ClientCreate(
            first_name=f"John{i}",
            last_name=f"Doe{i}",
            email=f"john{i}.doe@org1.com",
            organisation_id=org1.id,
        )
        create_client(session=db_session, client_create=client_create)

    for i in range(2):
        client_create = ClientCreate(
            first_name=f"Jane{i}",
            last_name=f"Smith{i}",
            email=f"jane{i}.smith@org2.com",
            organisation_id=org2.id,
        )
        create_client(session=db_session, client_create=client_create)

    results_org1 = get_clients_by_organisation(
        session=db_session, organisation_id=org1.id
    )
    results_org2 = get_clients_by_organisation(
        session=db_session, organisation_id=org2.id
    )

    assert len(results_org1) == 3
    assert len(results_org2) == 2
    assert all(result.organisation_id == org1.id for result in results_org1)
    assert all(result.organisation_id == org2.id for result in results_org2)
