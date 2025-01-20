import pytest
from app.organisations.models_permissions import Role, Resource, Permission
from app.organisations.utils_permissions import BasePermissionService


@pytest.fixture
def permission_service():
    return BasePermissionService()


def test_get_user_role(permission_service):
    """
    Test the retrieval of user roles.
    Scenario: Assign roles to users and verify correct retrieval.
    """
    permission_service.user_roles[(1, 1)] = Role.MANAGER
    permission_service.user_roles[(2, 1)] = Role.OPERATOR

    assert permission_service.get_user_role(1, 1) == Role.MANAGER
    assert permission_service.get_user_role(2, 1) == Role.OPERATOR
    assert permission_service.get_user_role(3, 1) is None


def test_get_role_permission(permission_service):
    """
    Test the retrieval of role permissions.
    Scenario: Check permissions for different role-resource combinations.
    """
    assert (
        permission_service.get_role_permission(Role.VIEWER, Resource.LOTS)
        == Permission.VIEW
    )
    assert (
        permission_service.get_role_permission(Role.MANAGER, Resource.USERS)
        == Permission.CREATE
    )
    assert (
        permission_service.get_role_permission(Role.OWNER, Resource.ORGANISATION)
        == Permission.DELETE
    )


def test_has_permission(permission_service):
    """
    Test the permission checking logic.
    Scenario: Set up user roles and check various permission scenarios.
    """
    permission_service.user_roles[(1, 1)] = Role.MANAGER
    permission_service.user_roles[(2, 1)] = Role.OPERATOR

    assert permission_service.has_permission(1, 1, Resource.LOTS, Permission.DELETE)
    assert permission_service.has_permission(2, 1, Resource.LOTS, Permission.CREATE)
    assert not permission_service.has_permission(2, 1, Resource.LOTS, Permission.DELETE)


def test_check_permission(permission_service):
    """
    Test the permission checking method that raises an exception.
    Scenario: Verify that appropriate exceptions are raised for insufficient permissions.
    """
    permission_service.user_roles[(1, 1)] = Role.OPERATOR

    with pytest.raises(PermissionError):
        BasePermissionService.check_permission(1, 1, Resource.USERS, Permission.CREATE)

    # This should not raise an exception
    BasePermissionService.check_permission(1, 1, Resource.LOTS, Permission.CREATE)


def test_permission_required_decorator():
    """
    Test the permission_required decorator.
    Scenario: Apply the decorator to a method and verify its behavior.
    """

    class TestService(BasePermissionService):
        @BasePermissionService.permission_required(Resource.LOTS, Permission.EDIT)
        def edit_lot(self, user_id: int, organisation_id: int):
            return "Lot edited"

    service = TestService()
    service.user_roles[(1, 1)] = Role.OPERATOR
    service.user_roles[(2, 1)] = Role.VIEWER

    assert service.edit_lot(1, 1) == "Lot edited"

    with pytest.raises(PermissionError):
        service.edit_lot(2, 1)


def test_role_hierarchy(permission_service):
    """
    Test the role hierarchy logic.
    Scenario: Verify that higher roles inherit permissions from lower roles.
    """
    permission_service.user_roles[(1, 1)] = Role.OWNER

    for resource in Resource:
        for permission in Permission:
            assert permission_service.has_permission(1, 1, resource, permission)


def test_cross_organisation_permissions(permission_service):
    """
    Test permissions across different organisations.
    Scenario: Set up a user with different roles in different organisations and verify permissions.
    """
    permission_service.user_roles[(1, 1)] = Role.MANAGER
    permission_service.user_roles[(1, 2)] = Role.OPERATOR

    assert permission_service.has_permission(1, 1, Resource.USERS, Permission.CREATE)
    assert not permission_service.has_permission(
        1, 2, Resource.USERS, Permission.CREATE
    )


def test_nonexistent_user(permission_service):
    """
    Test permission checking for non-existent users.
    Scenario: Verify that non-existent users have no permissions.
    """
    assert not permission_service.has_permission(
        999, 999, Resource.LOTS, Permission.VIEW
    )


def test_permission_order(permission_service):
    """
    Test the order of permissions.
    Scenario: Verify that higher permissions include lower permissions.
    """
    permission_service.user_roles[(1, 1)] = Role.MANAGER

    assert permission_service.has_permission(1, 1, Resource.LOTS, Permission.VIEW)
    assert permission_service.has_permission(1, 1, Resource.LOTS, Permission.EDIT)
    assert permission_service.has_permission(1, 1, Resource.LOTS, Permission.CREATE)
    assert permission_service.has_permission(1, 1, Resource.LOTS, Permission.DELETE)
