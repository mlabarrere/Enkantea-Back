import pytest
from app.lots.models import LotCreate, LotRead, LotUpdate
from app.core.exceptions import DatabaseOperationError, LotNotFoundError
from app.lots.CRUD import (
    create_lot,
    create_lots_batch,
    get_lot_by_id,
    update_lot,
    delete_lot,
)
from app.organisations.CRUD import create_organisation
from app.organisations.models_organisations import OrganisationCreate


def test_create_lot():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    # Test création de lot standard
    lot_create = LotCreate(
        name="Test Lot", description="A test lot", organisation_id=org.id
    )
    result = create_lot(lot_create)

    assert isinstance(result, LotRead)
    assert result.name == "Test Lot"
    assert result.description == "A test lot"
    assert result.organisation_id == org.id

    # Test création d'un lot avec le même nom (doublon)
    duplicate_lot = LotCreate(
        name="Test Lot", description="A duplicate lot", organisation_id=org.id
    )
    duplicate = create_lot(duplicate_lot)
    assert duplicate.name == "Test Lot"
    assert duplicate.description == "A duplicate lot"
    assert duplicate.organisation_id == org.id
    assert result.id != duplicate.id

    # Test création d'un lot avec des caractères spéciaux dans le nom
    special_char_lot = LotCreate(
        name="Test Lot #$%^&*",
        description="Lot with special characters",
        organisation_id=org.id,
    )
    special_result = create_lot(special_char_lot)
    assert special_result.name == "Test Lot #$%^&*"

    # Test création d'un lot avec une très longue description
    long_desc_lot = LotCreate(
        name="Long Description Lot",
        description="A" * 1000,  # 1000 caractères
        organisation_id=org.id,
    )
    long_result = create_lot(long_desc_lot)
    assert long_result.description == "A" * 1000


def test_create_lot_error():
    # Test création d'un lot avec un nom vide
    with pytest.raises(DatabaseOperationError):
        create_lot(LotCreate(name="", organisation_id=1))

    # Test création d'un lot avec une organisation inexistante
    with pytest.raises(DatabaseOperationError):
        create_lot(LotCreate(name="Invalid Org", organisation_id=999))

    # Test potentielle injection SQL dans le nom
    with pytest.raises(DatabaseOperationError):
        create_lot(LotCreate(name="Test'; DROP TABLE lots; --", organisation_id=1))


def test_create_lots_batch():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    # Test création en batch standard
    lots_create = [
        LotCreate(name="Lot 1", description="First lot", organisation_id=org.id),
        LotCreate(name="Lot 2", description="Second lot", organisation_id=org.id),
    ]
    results = create_lots_batch(lots_create)

    assert len(results) == 2
    assert all(isinstance(result, LotRead) for result in results)
    assert results[0].name == "Lot 1"
    assert results[1].name == "Lot 2"

    # Test création en batch avec un très grand nombre de lots
    many_lots = [
        LotCreate(name=f"Lot {i}", organisation_id=org.id) for i in range(1000)
    ]
    many_results = create_lots_batch(many_lots)
    assert len(many_results) == 1000


def test_get_lot_by_id():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    lot_create = LotCreate(
        name="Test Lot", description="A test lot", organisation_id=org.id
    )
    created_lot = create_lot(lot_create)

    result = get_lot_by_id(created_lot.id)

    assert isinstance(result, LotRead)
    assert result.name == "Test Lot"

    # Test récupération avec un ID négatif
    with pytest.raises(LotNotFoundError):
        get_lot_by_id(-1)


def test_update_lot():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    lot_create = LotCreate(
        name="Original Lot", description="Original description", organisation_id=org.id
    )
    created_lot = create_lot(lot_create)

    # Test mise à jour standard
    update_data = LotUpdate(name="Updated Lot", organisation_id=org.id)
    result = update_lot(created_lot.id, update_data)

    assert isinstance(result, LotRead)
    assert result.name == "Updated Lot"
    assert result.description == "Original description"


def test_delete_lot():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    lot_create = LotCreate(
        name="To Delete", description="This lot will be deleted", organisation_id=org.id
    )
    created_lot = create_lot(lot_create)

    result = delete_lot(created_lot.id)

    assert isinstance(result, LotRead)
    assert result.name == "To Delete"

    with pytest.raises(LotNotFoundError):
        get_lot_by_id(created_lot.id)

    # Test suppression d'un lot déjà supprimé
    with pytest.raises(LotNotFoundError):
        delete_lot(created_lot.id)
