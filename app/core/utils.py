from sqlmodel import select, Session
from app.organisations.models_permissions import UserOrganisationLink
from uuid import UUID


def is_user_authorized_for_organisation(
    session: Session, user_uuid: UUID, orga_uuid: UUID
) -> bool:
    """
    Check if the user is authorized to access the organisation.

    Args:
        session (Session): The database session.
        user_id (int): The user ID.
        organisation_id (int): The organisation ID.

    Returns:
        bool: True if the user is authorized, False otherwise.
    """
    statement = select(UserOrganisationLink).where(
        UserOrganisationLink.user_uuid == user_uuid,
        UserOrganisationLink.orga_uuid == orga_uuid,
    )
    result = session.exec(statement).first()
    return result is not None
