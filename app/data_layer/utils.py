from sqlmodel import select, Session
from app.models.users import UserOrganisationLink


def is_user_authorized_for_organisation(
    session: Session, user_id: int, organisation_id: int
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
        UserOrganisationLink.user_id == user_id,
        UserOrganisationLink.organisation_id == organisation_id,
    )
    result = session.exec(statement).first()
    return result is not None
