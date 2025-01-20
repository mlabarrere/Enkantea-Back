import pytest
from datetime import datetime, timezone
from app.sales.models import SaleCreate, SaleRead, SaleUpdate
from app.core.exceptions import SaleNotFoundError
from app.sales.CRUD import (
    create_sale,
    get_sale_by_id,
    update_sale,
    delete_sale,
    get_sales,
    get_sales_by_organisation,
)
from app.organisations.CRUD import create_organisation
from app.organisations.models_organisations import OrganisationCreate


def test_create_sale():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    sale_create = SaleCreate(
        number=1,
        title="Test Sale",
        description="Test Description",
        start_datetime=datetime.now(timezone.utc),
        end_datetime=datetime.now(timezone.utc),
        orga_uuid=org.uuid,
    )
    result = create_sale(sale_create=sale_create)

    assert isinstance(result, SaleRead)
    assert result.title == "Test Sale"
    assert result.description == "Test Description"
    assert result.orga_uuid == org.uuid


def test_get_sale_by_id():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    sale_create = SaleCreate(
        number=1,
        title="Test Sale",
        description="Test Description",
        start_datetime=datetime.now(timezone.utc),
        end_datetime=datetime.now(timezone.utc),
        orga_uuid=org.uuid,
    )
    created_sale = create_sale(sale_create=sale_create)

    result = get_sale_by_id(sale_id=created_sale.uuid)

    assert isinstance(result, SaleRead)
    assert result.uuid == created_sale.uuid
    assert result.title == "Test Sale"

    with pytest.raises(SaleNotFoundError):
        get_sale_by_id(sale_id=9999)


def test_update_sale():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    sale_create = SaleCreate(
        number=1,
        title="Original Sale",
        description="Original Description",
        start_datetime=datetime.now(timezone.utc),
        end_datetime=datetime.now(timezone.utc),
        orga_uuid=org.uuid,
    )
    created_sale = create_sale(sale_create=sale_create)

    update_data = SaleUpdate(title="Updated Sale", description="Updated Description")
    result = update_sale(sale_id=created_sale.uuid, sale_update=update_data)

    assert isinstance(result, SaleRead)
    assert result.title == "Updated Sale"
    assert result.description == "Updated Description"

    with pytest.raises(SaleNotFoundError):
        update_sale(sale_id=9999, sale_update=update_data)


def test_delete_sale():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    sale_create = SaleCreate(
        number=1,
        title="To Delete",
        description="This sale will be deleted",
        start_datetime=datetime.now(timezone.utc),
        end_datetime=datetime.now(timezone.utc),
        orga_uuid=org.uuid,
    )
    created_sale = create_sale(sale_create=sale_create)

    result = delete_sale(sale_id=created_sale.uuid)

    assert isinstance(result, SaleRead)
    assert result.title == "To Delete"

    with pytest.raises(SaleNotFoundError):
        get_sale_by_id(sale_id=created_sale.uuid)

    with pytest.raises(SaleNotFoundError):
        delete_sale(sale_id=created_sale.uuid)


def test_get_sales():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    for i in range(5):
        sale_create = SaleCreate(
            number=i + 1,
            title=f"Test Sale {i+1}",
            description=f"Description {i+1}",
            start_datetime=datetime.now(timezone.utc),
            end_datetime=datetime.now(timezone.utc),
            orga_uuid=org.uuid,
        )
        create_sale(sale_create=sale_create)

    results = get_sales(skip=0, limit=10)

    assert len(results) == 5
    assert all(isinstance(result, SaleRead) for result in results)


def test_get_sales_by_organisation():
    org_create1 = OrganisationCreate(name="Test Organisation 1")
    org1 = create_organisation(organisation_create=org_create1)

    org_create2 = OrganisationCreate(name="Test Organisation 2")
    org2 = create_organisation(organisation_create=org_create2)

    for i in range(3):
        sale_create = SaleCreate(
            number=i + 1,
            title=f"Org1 Sale {i+1}",
            description=f"Description {i+1}",
            start_datetime=datetime.now(timezone.utc),
            end_datetime=datetime.now(timezone.utc),
            orga_uuid=org1.uuid,
        )
        create_sale(sale_create=sale_create)

    for i in range(2):
        sale_create = SaleCreate(
            number=i + 1,
            title=f"Org2 Sale {i+1}",
            description=f"Description {i+1}",
            start_datetime=datetime.now(timezone.utc),
            end_datetime=datetime.now(timezone.utc),
            orga_uuid=org2.uuid,
        )
        create_sale(sale_create=sale_create)

    results_org1 = get_sales_by_organisation(orga_uuid=org1.uuid)
    results_org2 = get_sales_by_organisation(orga_uuid=org2.uuid)

    assert len(results_org1) == 3
    assert len(results_org2) == 2
    assert all(result.orga_uuid == org1.uuid for result in results_org1)
    assert all(result.orga_uuid == org2.uuid for result in results_org2)
