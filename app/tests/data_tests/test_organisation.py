import pytest
from app.models.organisations import (
    OrganisationCreate,
    OrganisationRead,
    OrganisationUpdate,
    CompanyType,
)
from app.core.exceptions import OrganisationNotFoundError
from app.data_layer.organisations import (
    create_organisation,
    update_organisation,
    get_organisation_by_id,
    delete_organisation,
)
from datetime import datetime


def test_create_organisation():
    org_create = OrganisationCreate(
        name="Test Organisation",
        organisation_type=CompanyType.SA,
        siren_number=123456789,
        ape_code="6201Z",
        share_capital=10000.0,
        start_date=datetime(2020, 1, 1),
        registration_date=datetime(2020, 1, 1),
        headquarter_siret_number="12345678900010",
        address="123 Test St",
        postal_code="75000",
        city="Paris",
    )
    result = create_organisation(organisation_create=org_create)

    assert isinstance(result, OrganisationRead)
    assert result.name == "Test Organisation"
    assert result.organisation_type == CompanyType.SA
    assert result.siren_number == 123456789

    # Test création avec des champs minimaux
    min_org = OrganisationCreate(name="Minimal Org")
    min_result = create_organisation(organisation_create=min_org)
    assert isinstance(min_result, OrganisationRead)
    assert min_result.name == "Minimal Org"


def test_get_organisation_by_id():
    org_create = OrganisationCreate(name="Test Organisation")
    created_org = create_organisation(
        organisation_create=org_create
    )

    result = get_organisation_by_id(organisation_id=created_org.id)

    assert isinstance(result, OrganisationRead)
    assert result.name == "Test Organisation"

    with pytest.raises(OrganisationNotFoundError):
        get_organisation_by_id(organisation_id=9999)


def test_update_organisation():
    org_create = OrganisationCreate(name="Original Organisation")
    created_org = create_organisation(
        organisation_create=org_create
    )

    update_data = OrganisationUpdate(
        name="Updated Organisation", organisation_type=CompanyType.SARL
    )
    result = update_organisation(
        
        organisation_id=created_org.id,
        organisation_update=update_data,
    )

    assert isinstance(result, OrganisationRead)
    assert result.name == "Updated Organisation"
    assert result.organisation_type == CompanyType.SARL

    # Test mise à jour partielle
    partial_update = OrganisationUpdate(siren_number=987654321)
    partial_result = update_organisation(
        
        organisation_id=created_org.id,
        organisation_update=partial_update,
    )
    assert partial_result.name == "Updated Organisation"
    assert partial_result.siren_number == 987654321

    with pytest.raises(OrganisationNotFoundError):
        update_organisation(
            
            organisation_id=9999,
            organisation_update=OrganisationUpdate(name="Nonexistent"),
        )


def test_delete_organisation():
    org_create = OrganisationCreate(name="To Delete")
    created_org = create_organisation(
        organisation_create=org_create
    )

    result = delete_organisation(organisation_id=created_org.id)

    assert isinstance(result, OrganisationRead)
    assert result.name == "To Delete"

    with pytest.raises(OrganisationNotFoundError):
        get_organisation_by_id(organisation_id=created_org.id)

    with pytest.raises(OrganisationNotFoundError):
        delete_organisation(organisation_id=created_org.id)