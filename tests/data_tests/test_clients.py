import pytest
from app.clients.models import ClientCreate, ClientRead, ClientUpdate
from app.core.exceptions import ClientNotFoundError
from app.clients.CRUD import (
    create_client,
    get_client_by_uuid,
    update_client,
    delete_client,
    get_clients_by_organisation,
)
from app.organisations.CRUD import create_organisation
from app.organisations.models_organisations import OrganisationCreate


def test_create_client():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    client_create = ClientCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        orga_uuid=org.uuid,
    )
    result = create_client(client_create=client_create)

    assert isinstance(result, ClientRead)
    assert result.first_name == "John"
    assert result.last_name == "Doe"
    assert result.email == "john.doe@example.com"
    assert result.orga_uuid == org.uuid


def test_get_client_by_uuid():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    client_create = ClientCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        orga_uuid=org.uuid,
    )
    created_client = create_client(client_create=client_create)

    result = get_client_by_uuid(client_id=created_client.id)

    assert isinstance(result, ClientRead)
    assert result.id == created_client.id
    assert result.first_name == "John"

    with pytest.raises(ClientNotFoundError):
        get_client_by_uuid(client_id=9999)


def test_update_client():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    client_create = ClientCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        orga_uuid=org.uuid,
    )
    created_client = create_client(client_create=client_create)

    update_data = ClientUpdate(first_name="Jane", email="jane.doe@example.com")
    result = update_client(client_id=created_client.id, client_update=update_data)

    assert isinstance(result, ClientRead)
    assert result.first_name == "Jane"
    assert result.email == "jane.doe@example.com"
    assert result.last_name == "Doe"  # Unchanged

    with pytest.raises(ClientNotFoundError):
        update_client(client_id=9999, client_update=update_data)


def test_delete_client():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    client_create = ClientCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        orga_uuid=org.uuid,
    )
    created_client = create_client(client_create=client_create)

    result = delete_client(client_id=created_client.id)

    assert isinstance(result, ClientRead)
    assert result.first_name == "John"

    with pytest.raises(ClientNotFoundError):
        get_client_by_uuid(client_id=created_client.id)

    with pytest.raises(ClientNotFoundError):
        delete_client(client_id=created_client.id)


def test_get_clients_by_organisation():
    org_create1 = OrganisationCreate(name="Test Organisation 1")
    org1 = create_organisation(organisation_create=org_create1)

    org_create2 = OrganisationCreate(name="Test Organisation 2")
    org2 = create_organisation(organisation_create=org_create2)

    for i in range(3):
        client_create = ClientCreate(
            first_name=f"John{i}",
            last_name=f"Doe{i}",
            email=f"john{i}.doe@org1.com",
            orga_uuid=org1.uuid,
        )
        create_client(client_create=client_create)

    for i in range(2):
        client_create = ClientCreate(
            first_name=f"Jane{i}",
            last_name=f"Smith{i}",
            email=f"jane{i}.smith@org2.com",
            orga_uuid=org2.uuid,
        )
        create_client(client_create=client_create)

    results_org1 = get_clients_by_organisation(orga_uuid=org1.uuid)
    results_org2 = get_clients_by_organisation(orga_uuid=org2.uuid)

    assert len(results_org1) == 3
    assert len(results_org2) == 2
    assert all(result.orga_uuid == org1.uuid for result in results_org1)
    assert all(result.orga_uuid == org2.uuid for result in results_org2)
