from uuid import UUID
from sqlmodel import select
from app.organisations.models_organisations import (
    Organisation,
    OrganisationCreate,
    OrganisationUpdate,
    OrganisationRead,
)
from app.users.models import User, UserRead
from app.core.exceptions import (
    DatabaseOperationError,
    OrganisationNotFoundError,
    UserNotFoundError,
)
from app.organisations.models_permissions import UserRole, UserOrganisationLink
from app.core.database import get_db_session


async def create_organisation(
    organisation_create: OrganisationCreate,
) -> OrganisationRead:
    """
    Create a new organisation in the database.

    This function performs a pure CRUD operation to create an organisation.
    Authorization checks should be done in the service layer before calling this function.

    Args:

        organisation_create (OrganisationCreate): The organisation data to create.

    Returns:
        OrganisationRead: The created organisation data.

    Raises:
        DatabaseOperationError: If an error occurs during organisation creation.
    """
    with get_db_session() as session:
        try:
            organisation = Organisation.model_validate(organisation_create)
            session.add(organisation)
            session.commit()
            session.refresh(organisation)
            return OrganisationRead.model_validate(organisation)
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(f"Failed to create organisation: {str(e)}")


async def update_organisation(
    orga_uuid: UUID, organisation_update: OrganisationUpdate
) -> OrganisationRead:
    """
    Update an existing organisation in the database.

    Args:

        orga_uuid (int): The ID of the organisation to update.
        organisation_update (OrganisationUpdate): The updated organisation data.

    Returns:
        OrganisationRead: The updated organisation data.

    Raises:
        OrganisationNotFoundError: If the organisation is not found.
        DatabaseOperationError: If an error occurs during the update operation.
    """
    with get_db_session() as session:
        try:
            db_organisation = session.get(Organisation, orga_uuid)
            if not db_organisation:
                raise OrganisationNotFoundError(
                    f"Organisation with id {orga_uuid} not found"
                )

            organisation_data = organisation_update.model_dump(exclude_unset=True)
            for key, value in organisation_data.items():
                setattr(db_organisation, key, value)

            session.add(db_organisation)
            session.commit()
            session.refresh(db_organisation)
            return OrganisationRead.model_validate(db_organisation)
        except OrganisationNotFoundError:
            raise
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(f"Failed to update organisation: {str(e)}")


async def get_organisation_by_id(orga_uuid: UUID) -> OrganisationRead:
    """
    Retrieve an organisation by its ID.

    Args:

        orga_uuid (int): The ID of the organisation to retrieve.

    Returns:
        OrganisationRead: The retrieved organisation data.

    Raises:
        OrganisationNotFoundError: If the organisation is not found.
    """
    with get_db_session() as session:
        organisation = session.get(Organisation, orga_uuid)
        if not organisation:
            raise OrganisationNotFoundError(
                f"Organisation with id {orga_uuid} not found"
            )
        return OrganisationRead.model_validate(organisation)


async def delete_organisation(orga_uuid: UUID) -> OrganisationRead:
    """
    Delete an organisation from the database.

    Args:

        orga_uuid (int): The ID of the organisation to delete.

    Returns:
        OrganisationRead: The deleted organisation data.

    Raises:
        OrganisationNotFoundError: If the organisation is not found.
        DatabaseOperationError: If an error occurs during the delete operation.
    """
    with get_db_session() as session:
        try:
            organisation = session.get(Organisation, orga_uuid)
            if not organisation:
                raise OrganisationNotFoundError(
                    f"Organisation with id {orga_uuid} not found"
                )

            session.delete(organisation)
            session.commit()
            return OrganisationRead.model_validate(organisation)
        except OrganisationNotFoundError:
            raise
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(f"Failed to delete organisation: {str(e)}")


async def get_members_from_organisation(orga_uuid: UUID) -> list[UserRead]:
    """
    Retrieve all members of an organisation.

    Args:

        orga_uuid (int): The ID of the organisation.

    Returns:
        list[UserRead]: A list of users who are members of the organisation.

    Raises:
        OrganisationNotFoundError: If the organisation is not found.
    """
    with get_db_session() as session:
        organisation = session.get(Organisation, orga_uuid)
        if not organisation:
            raise OrganisationNotFoundError(
                f"Organisation with id {orga_uuid} not found"
            )

        statement = (
            select(User, UserRole)
            .join(UserOrganisationLink)
            .where(UserOrganisationLink.orga_uuid == orga_uuid)
        )
        results = session.exec(statement).all()
        return [UserRead.model_validate(user) for user, _ in results]


async def add_member_to_organisation(
    user_uuid: UUID, orga_uuid: UUID, role: UserRole
) -> UserOrganisationLink:
    """
    Add a user as a member of an organisation.

    Args:

        user_uuid (int): The ID of the user to add.
        orga_uuid (int): The ID of the organisation.
        role (UserRole): The role of the user in the organisation.

    Returns:
        UserOrganisationLink: The created link between user and organisation.

    Raises:
        UserNotFoundError: If the user is not found.
        OrganisationNotFoundError: If the organisation is not found.
        DatabaseOperationError: If an error occurs during the operation.
    """
    with get_db_session() as session:
        try:
            user = session.get(User, user_uuid)
            if not user:
                raise UserNotFoundError(f"User with id {user_uuid} not found")

            organisation = session.get(Organisation, orga_uuid)
            if not organisation:
                raise OrganisationNotFoundError(
                    f"Organisation with id {orga_uuid} not found"
                )

            statement = select(UserOrganisationLink).where(
                UserOrganisationLink.user_uuid == user_uuid,
                UserOrganisationLink.orga_uuid == orga_uuid,
            )
            existing_link = session.exec(statement).first()
            if existing_link:
                raise DatabaseOperationError(
                    "User is already a member of this organisation"
                )

            user_org_link = UserOrganisationLink(
                user_uuid=user_uuid, orga_uuid=orga_uuid, role=role
            )
            session.add(user_org_link)
            session.commit()
            session.refresh(user_org_link)

            return user_org_link
        except (UserNotFoundError, OrganisationNotFoundError):
            raise
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(
                f"Failed to add member to organisation: {str(e)}"
            )


async def remove_member_from_organisation(user_uuid: UUID, orga_uuid: UUID) -> None:
    """
    Remove a user from an organisation.

    Args:

        user_uuid (int): The ID of the user to remove.
        orga_uuid (int): The ID of the organisation.

    Raises:
        DatabaseOperationError: If an error occurs during the operation or if trying to remove the owner.
    """
    with get_db_session() as session:
        try:
            user_org_link = session.get(UserOrganisationLink, (user_uuid, orga_uuid))
            if not user_org_link:
                raise DatabaseOperationError(
                    "User is not a member of this organisation"
                )

            if user_org_link.role == UserRole.OWNER:
                raise DatabaseOperationError(
                    "Cannot remove the owner of the organisation"
                )

            session.delete(user_org_link)
            session.commit()
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(
                f"Failed to remove member from organisation: {str(e)}"
            )
