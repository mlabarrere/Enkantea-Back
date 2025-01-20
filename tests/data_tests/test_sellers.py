import pytest
from app.sellers.models import SellerCreate, SellerRead, SellerUpdate
from app.core.exceptions import SellerNotFoundError
from app.sellers.CRUD import (
    create_seller,
    get_seller_by_id,
    update_seller,
    delete_seller,
    get_sellers,
    get_sellers_by_organisation,
)
from app.organisations.CRUD import create_organisation
from app.organisations.models_organisations import OrganisationCreate


def test_create_seller():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    seller_create = SellerCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="1234567890",
        orga_uuid=org.uuid,
        professional=True,
    )
    result = create_seller(seller_create=seller_create)

    assert isinstance(result, SellerRead)
    assert result.first_name == "John"
    assert result.last_name == "Doe"
    assert result.email == "john.doe@example.com"
    assert result.phone == "1234567890"
    assert result.orga_uuid == org.uuid
    assert result.professional


def test_get_seller_by_id():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    seller_create = SellerCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        orga_uuid=org.uuid,
    )
    created_seller = create_seller(seller_create=seller_create)

    result = get_seller_by_id(seller_id=created_seller.uuid)

    assert isinstance(result, SellerRead)
    assert result.uuid == created_seller.uuid
    assert result.first_name == "John"

    with pytest.raises(SellerNotFoundError):
        get_seller_by_id(seller_id=9999)


def test_update_seller():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    seller_create = SellerCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        orga_uuid=org.uuid,
    )
    created_seller = create_seller(seller_create=seller_create)

    update_data = SellerUpdate(
        first_name="Jane", email="jane.doe@example.com", professional=True
    )
    result = update_seller(seller_id=created_seller.uuid, seller_update=update_data)

    assert isinstance(result, SellerRead)
    assert result.first_name == "Jane"
    assert result.email == "jane.doe@example.com"
    assert result.last_name == "Doe"  # Unchanged
    assert result.professional

    with pytest.raises(SellerNotFoundError):
        update_seller(seller_id=9999, seller_update=update_data)


def test_delete_seller():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    seller_create = SellerCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        orga_uuid=org.uuid,
    )
    created_seller = create_seller(seller_create=seller_create)

    result = delete_seller(seller_id=created_seller.uuid)

    assert isinstance(result, SellerRead)
    assert result.first_name == "John"

    with pytest.raises(SellerNotFoundError):
        get_seller_by_id(seller_id=created_seller.uuid)

    with pytest.raises(SellerNotFoundError):
        delete_seller(seller_id=created_seller.uuid)


def test_get_sellers():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    for i in range(5):
        seller_create = SellerCreate(
            first_name=f"John{i}",
            last_name=f"Doe{i}",
            email=f"john{i}.doe@example.com",
            orga_uuid=org.uuid,
        )
        create_seller(seller_create=seller_create)

    results = get_sellers(skip=0, limit=10)

    assert len(results) == 5
    assert all(isinstance(result, SellerRead) for result in results)


def test_get_sellers_by_organisation():
    org_create1 = OrganisationCreate(name="Test Organisation 1")
    org1 = create_organisation(organisation_create=org_create1)

    org_create2 = OrganisationCreate(name="Test Organisation 2")
    org2 = create_organisation(organisation_create=org_create2)

    for i in range(3):
        seller_create = SellerCreate(
            first_name=f"John{i}",
            last_name=f"Doe{i}",
            email=f"john{i}.doe@org1.com",
            orga_uuid=org1.uuid,
        )
        create_seller(seller_create=seller_create)

    for i in range(2):
        seller_create = SellerCreate(
            first_name=f"Jane{i}",
            last_name=f"Smith{i}",
            email=f"jane{i}.smith@org2.com",
            orga_uuid=org2.uuid,
        )
        create_seller(seller_create=seller_create)

    results_org1 = get_sellers_by_organisation(orga_uuid=org1.uuid)
    results_org2 = get_sellers_by_organisation(orga_uuid=org2.uuid)

    assert len(results_org1) == 3
    assert len(results_org2) == 2
    assert all(result.orga_uuid == org1.uuid for result in results_org1)
    assert all(result.orga_uuid == org2.uuid for result in results_org2)
