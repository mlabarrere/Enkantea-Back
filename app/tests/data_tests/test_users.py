import pytest
from app.models.users import UserCreate, UserRead, UserUpdate
from app.core.exceptions import UserNotFoundError
from app.data_layer.users import (
    create_user,
    get_user_by_id,
    get_user_by_email,
    update_user,
    delete_user,
    get_users,
    get_users_by_organisation,
)
from app.data_layer.organisations import create_organisation
from app.models.organisations import OrganisationCreate


def test_create_user():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    user_create = UserCreate(
        email="john.doe@example.com",
        password="password123",
        first_name="John",
        last_name="Doe",
        organisation_id=org.id,
    )
    result = create_user(user_create=user_create)

    assert isinstance(result, UserRead)
    assert result.email == "john.doe@example.com"
    assert result.first_name == "John"
    assert result.last_name == "Doe"
    assert result.organisation_id == org.id
    assert not hasattr(result, "password")


def test_get_user_by_id():
    org_create = OrganisationCreate(name="Test Organisation")
    org = create_organisation(organisation_create=org_create)

    user_create = UserCreate(
        email="john.doe@example.com",
        password="password123",
        first_name="John",
        last_name="Doe",
        organisation_id=org.id,
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
        organisation_id=org.id,
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
        organisation_id=org.id,
    )
    created_user = create_user(user_create=user_create)

    update_data = UserUpdate(first_name="Jane", last_name="Smith")
    result = update_user(
        user_id=created_user.id, user_update=update_data
    )

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
        organisation_id=org.id,
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
            organisation_id=org.id,
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
            organisation_id=org1.id,
        )
        create_user(user_create=user_create)

    for i in range(2):
        user_create = UserCreate(
            email=f"user{i}@org2.com",
            password="password123",
            first_name=f"User{i}",
            last_name="Org2",
            organisation_id=org2.id,
        )
        create_user(user_create=user_create)

    results_org1 = get_users_by_organisation(
        organisation_id=org1.id
    )
    results_org2 = get_users_by_organisation(
        organisation_id=org2.id
    )

    assert len(results_org1) == 3
    assert len(results_org2) == 2
    assert all(result.organisation_id == org1.id for result in results_org1)
    assert all(result.organisation_id == org2.id for result in results_org2)