import pytest
from app.models.sellers import SellerCreate, SellerRead, SellerUpdate
from app.core.exceptions import SellerNotFoundError
from app.data_layer.sellers import (
    create_seller,
    get_seller_by_id,
    update_seller,
    delete_seller,
    get_sellers,
    get_sellers_by_organisation,
)
from app.data_layer.organisations import create_organisation
from app.models.organisations import OrganisationCreate


def test_create_seller():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    seller_create = SellerCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="1234567890",
        organisation_id=org.id,
        professional=True,
    )
    result = create_seller(seller_create=seller_create)

    assert isinstance(result, SellerRead)
    assert result.first_name == "John"
    assert result.last_name == "Doe"
    assert result.email == "john.doe@example.com"
    assert result.phone == "1234567890"
    assert result.organisation_id == org.id
    assert result.professional


def test_get_seller_by_id():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    seller_create = SellerCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        organisation_id=org.id,
    )
    created_seller = create_seller(seller_create=seller_create)

    result = get_seller_by_id(seller_id=created_seller.id)

    assert isinstance(result, SellerRead)
    assert result.id == created_seller.id
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
        organisation_id=org.id,
    )
    created_seller = create_seller(seller_create=seller_create)

    update_data = SellerUpdate(
        first_name="Jane", email="jane.doe@example.com", professional=True
    )
    result = update_seller(
        seller_id=created_seller.id, seller_update=update_data
    )

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
        organisation_id=org.id,
    )
    created_seller = create_seller(seller_create=seller_create)

    result = delete_seller(seller_id=created_seller.id)

    assert isinstance(result, SellerRead)
    assert result.first_name == "John"

    with pytest.raises(SellerNotFoundError):
        get_seller_by_id(seller_id=created_seller.id)

    with pytest.raises(SellerNotFoundError):
        delete_seller(seller_id=created_seller.id)


def test_get_sellers():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    for i in range(5):
        seller_create = SellerCreate(
            first_name=f"John{i}",
            last_name=f"Doe{i}",
            email=f"john{i}.doe@example.com",
            organisation_id=org.id,
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
            organisation_id=org1.id,
        )
        create_seller(seller_create=seller_create)

    for i in range(2):
        seller_create = SellerCreate(
            first_name=f"Jane{i}",
            last_name=f"Smith{i}",
            email=f"jane{i}.smith@org2.com",
            organisation_id=org2.id,
        )
        create_seller(seller_create=seller_create)

    results_org1 = get_sellers_by_organisation(
        organisation_id=org1.id
    )
    results_org2 = get_sellers_by_organisation(
        organisation_id=org2.id
    )

    assert len(results_org1) == 3
    assert len(results_org2) == 2
    assert all(result.organisation_id == org1.id for result in results_org1)
    assert all(result.organisation_id == org2.id for result in results_org2)