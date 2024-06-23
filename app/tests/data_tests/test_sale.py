import pytest
from datetime import datetime, timezone
from app.models.sales import SaleCreate, SaleRead, SaleUpdate
from app.core.exceptions import SaleNotFoundError
from app.data_layer.sales import (
    create_sale,
    get_sale_by_id,
    update_sale,
    delete_sale,
    get_sales,
    get_sales_by_organisation,
)
from app.data_layer.organisations import create_organisation
from app.models.organisations import OrganisationCreate


def test_create_sale(db_session):
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(session=db_session, organisation_create=org_create)

    sale_create = SaleCreate(
        number=1,
        title="Test Sale",
        description="Test Description",
        start_datetime=datetime.now(timezone.utc),
        end_datetime=datetime.now(timezone.utc),
        organisation_id=org.id,
    )
    result = create_sale(session=db_session, sale_create=sale_create)

    assert isinstance(result, SaleRead)
    assert result.title == "Test Sale"
    assert result.description == "Test Description"
    assert result.organisation_id == org.id


def test_get_sale_by_id(db_session):
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(session=db_session, organisation_create=org_create)

    sale_create = SaleCreate(
        number=1,
        title="Test Sale",
        description="Test Description",
        start_datetime=datetime.now(timezone.utc),
        end_datetime=datetime.now(timezone.utc),
        organisation_id=org.id,
    )
    created_sale = create_sale(session=db_session, sale_create=sale_create)

    result = get_sale_by_id(session=db_session, sale_id=created_sale.id)

    assert isinstance(result, SaleRead)
    assert result.id == created_sale.id
    assert result.title == "Test Sale"

    with pytest.raises(SaleNotFoundError):
        get_sale_by_id(session=db_session, sale_id=9999)


def test_update_sale(db_session):
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(session=db_session, organisation_create=org_create)

    sale_create = SaleCreate(
        number=1,
        title="Original Sale",
        description="Original Description",
        start_datetime=datetime.now(timezone.utc),
        end_datetime=datetime.now(timezone.utc),
        organisation_id=org.id,
    )
    created_sale = create_sale(session=db_session, sale_create=sale_create)

    update_data = SaleUpdate(title="Updated Sale", description="Updated Description")
    result = update_sale(
        session=db_session, sale_id=created_sale.id, sale_update=update_data
    )

    assert isinstance(result, SaleRead)
    assert result.title == "Updated Sale"
    assert result.description == "Updated Description"

    with pytest.raises(SaleNotFoundError):
        update_sale(session=db_session, sale_id=9999, sale_update=update_data)


def test_delete_sale(db_session):
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(session=db_session, organisation_create=org_create)

    sale_create = SaleCreate(
        number=1,
        title="To Delete",
        description="This sale will be deleted",
        start_datetime=datetime.now(timezone.utc),
        end_datetime=datetime.now(timezone.utc),
        organisation_id=org.id,
    )
    created_sale = create_sale(session=db_session, sale_create=sale_create)

    result = delete_sale(session=db_session, sale_id=created_sale.id)

    assert isinstance(result, SaleRead)
    assert result.title == "To Delete"

    with pytest.raises(SaleNotFoundError):
        get_sale_by_id(session=db_session, sale_id=created_sale.id)

    with pytest.raises(SaleNotFoundError):
        delete_sale(session=db_session, sale_id=created_sale.id)


def test_get_sales(db_session):
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(session=db_session, organisation_create=org_create)

    for i in range(5):
        sale_create = SaleCreate(
            number=i + 1,
            title=f"Test Sale {i+1}",
            description=f"Description {i+1}",
            start_datetime=datetime.now(timezone.utc),
            end_datetime=datetime.now(timezone.utc),
            organisation_id=org.id,
        )
        create_sale(session=db_session, sale_create=sale_create)

    results = get_sales(session=db_session, skip=0, limit=10)

    assert len(results) == 5
    assert all(isinstance(result, SaleRead) for result in results)


def test_get_sales_by_organisation(db_session):
    org_create1 = OrganisationCreate(name="Test Organisation 1")
    org1 = create_organisation(session=db_session, organisation_create=org_create1)

    org_create2 = OrganisationCreate(name="Test Organisation 2")
    org2 = create_organisation(session=db_session, organisation_create=org_create2)

    for i in range(3):
        sale_create = SaleCreate(
            number=i + 1,
            title=f"Org1 Sale {i+1}",
            description=f"Description {i+1}",
            start_datetime=datetime.now(timezone.utc),
            end_datetime=datetime.now(timezone.utc),
            organisation_id=org1.id,
        )
        create_sale(session=db_session, sale_create=sale_create)

    for i in range(2):
        sale_create = SaleCreate(
            number=i + 1,
            title=f"Org2 Sale {i+1}",
            description=f"Description {i+1}",
            start_datetime=datetime.now(timezone.utc),
            end_datetime=datetime.now(timezone.utc),
            organisation_id=org2.id,
        )
        create_sale(session=db_session, sale_create=sale_create)

    results_org1 = get_sales_by_organisation(
        session=db_session, organisation_id=org1.id
    )
    results_org2 = get_sales_by_organisation(
        session=db_session, organisation_id=org2.id
    )

    assert len(results_org1) == 3
    assert len(results_org2) == 2
    assert all(result.organisation_id == org1.id for result in results_org1)
    assert all(result.organisation_id == org2.id for result in results_org2)
