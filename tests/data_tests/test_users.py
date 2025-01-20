import pytest
from app.users.models import UserCreate, UserRead, UserUpdate
from app.core.exceptions import UserNotFoundError
from app.users.CRUD import (
    create_user,
    get_user_by_uuid,
    get_user_by_email,
    update_user,
    delete_user,
    get_users,
    get_users_by_organisation,
)
from app.organisations.CRUD import create_organisation
from app.organisations.models_organisations import OrganisationCreate


def test_create_user():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    user_create = UserCreate(
        email="john.doe@example.com",
        password="password123",
        first_name="John",
        last_name="Doe",
        current_orga_uuid=org.uuid,
    )
    result = create_user(user_create=user_create)

    assert isinstance(result, UserRead)
    assert result.email == "john.doe@example.com"
    assert result.first_name == "John"
    assert result.last_name == "Doe"
    assert result.orga_uuid == org.uuid
    assert not hasattr(result, "password")


def test_get_user_by_id():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    user_create = UserCreate(
        email="john.doe@example.com",
        password="password123",
        first_name="John",
        last_name="Doe",
        current_orga_uuid=org.uuid,
    )
    created_user = create_user(user_create=user_create)

    result = get_user_by_id(user_id=created_user.id)

    assert isinstance(result, UserRead)
    assert result.id == created_user.id
    assert result.email == "john.doe@example.com"

    with pytest.raises(UserNotFoundError):
        get_user_by_id(user_id=9999)


def test_get_user_by_email():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    user_create = UserCreate(
        email="john.doe@example.com",
        password="password123",
        first_name="John",
        last_name="Doe",
        current_orga_uuid=org.uuid,
    )
    create_user(user_create=user_create)

    result = get_user_by_email(email="john.doe@example.com")

    assert isinstance(result, UserRead)
    assert result.email == "john.doe@example.com"

    with pytest.raises(UserNotFoundError):
        get_user_by_email(email="nonexistent@example.com")


def test_update_user():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    user_create = UserCreate(
        email="john.doe@example.com",
        password="password123",
        first_name="John",
        last_name="Doe",
        current_orga_uuid=org.uuid,
    )
    created_user = create_user(user_create=user_create)

    update_data = UserUpdate(first_name="Jane", last_name="Smith")
    result = update_user(user_id=created_user.id, user_update=update_data)

    assert isinstance(result, UserRead)
    assert result.first_name == "Jane"
    assert result.last_name == "Smith"
    assert result.email == "john.doe@example.com"  # Unchanged

    with pytest.raises(UserNotFoundError):
        update_user(user_id=9999, user_update=update_data)


def test_delete_user():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    user_create = UserCreate(
        email="john.doe@example.com",
        password="password123",
        first_name="John",
        last_name="Doe",
        current_orga_uuid=org.uuid,
    )
    created_user = create_user(user_create=user_create)

    result = delete_user(user_id=created_user.id)

    assert isinstance(result, UserRead)
    assert result.email == "john.doe@example.com"

    with pytest.raises(UserNotFoundError):
        get_user_by_id(user_id=created_user.id)

    with pytest.raises(UserNotFoundError):
        delete_user(user_id=created_user.id)


def test_get_users():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    for i in range(5):
        user_create = UserCreate(
            email=f"user{i}@example.com",
            password="password123",
            first_name=f"User{i}",
            last_name="Test",
            current_orga_uuid=org.uuid,
        )
        create_user(user_create=user_create)

    results = get_users(skip=0, limit=10)

    assert len(results) == 5
    assert all(isinstance(result, UserRead) for result in results)


def test_get_users_by_organisation():
    org_create1 = OrganisationCreate(name="Test Organisation 1")
    org1 = create_organisation(organisation_create=org_create1)

    org_create2 = OrganisationCreate(name="Test Organisation 2")
    org2 = create_organisation(organisation_create=org_create2)

    for i in range(3):
        user_create = UserCreate(
            email=f"user{i}@org1.com",
            password="password123",
            first_name=f"User{i}",
            last_name="Org1",
            current_orga_uuid=org1.uuid,
        )
        create_user(user_create=user_create)

    for i in range(2):
        user_create = UserCreate(
            email=f"user{i}@org2.com",
            password="password123",
            first_name=f"User{i}",
            last_name="Org2",
            current_orga_uuid=org2.uuid,
        )
        create_user(user_create=user_create)

    results_org1 = get_users_by_organisation(orga_uuid=org1.uuid)
    results_org2 = get_users_by_organisation(orga_uuid=org2.uuid)

    assert len(results_org1) == 3
    assert len(results_org2) == 2
    assert all(result.orga_uuid == org1.uuid for result in results_org1)
    assert all(result.orga_uuid == org2.uuid for result in results_org2)
