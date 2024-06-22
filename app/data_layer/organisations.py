from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.models.organisations import (
    Organisation,
    OrganisationCreate,
    OrganisationUpdate,
    OrganisationRead,
    UserRole,
    UserOrganisationLink
)
from app.models.users import User, UserRead


async def create_organisation(organisation_create: OrganisationCreate, session: Session) -> OrganisationRead:
    try:
        session.add(organisation_create)
        session.commit()
        session.refresh(organisation_create)
        return organisation_create
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the organisation: {str(e)}",
        )


async def update_organisation(
    *,
    session: Session,
    db_organisation: Organisation,
    organisation_in: OrganisationUpdate,
) -> OrganisationRead:
    try:
        organisation_data = organisation_in.model_dump(exclude_unset=True)
        db_organisation.sqlmodel_update(organisation_data)
        session.add(db_organisation)
        session.commit()
        session.refresh(db_organisation)
        return db_organisation
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the organisation: {str(e)}",
        )


async def get_organisation_by_id(*, session: Session, organisation_id: int) -> OrganisationRead | None:
    try:
        organisation = session.get(Organisation, organisation_id)
        if not organisation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found")
        return organisation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the organisation by ID: {str(e)}",
        )


async def get_organisation_by_name(*, session: Session, company_name: str) -> OrganisationRead | None:
    try:
        statement = select(Organisation).where(Organisation.company_name == company_name)
        organisation = session.exec(statement).first()
        if not organisation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found")
        return organisation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the organisation by name: {str(e)}",
        )


async def delete_organisation(*, session: Session, organisation_id: int) -> OrganisationRead | None:
    try:
        db_organisation = session.get(Organisation, organisation_id)
        if not db_organisation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found")
        session.delete(db_organisation)
        session.commit()
        return db_organisation
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the organisation: {str(e)}",
        )

async def get_members_from_organisation(*, session: Session, organisation_id: int) -> list[UserRead]:
    statement = select(User, UserRole).join(UserOrganisationLink).where(UserOrganisationLink.organisation_id == organisation_id)
    return session.exec(statement).all()


async def add_member_to_organisation(session: Session, user_id: int, organisation_id: int, role: UserRole) -> UserOrganisationLink:
    try:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        organisation = session.get(Organisation, organisation_id)
        if not organisation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found"
            )

        statement = select(UserOrganisationLink).where(
            UserOrganisationLink.user_id == user_id,
            UserOrganisationLink.organisation_id == organisation_id,
        )
        existing_link = session.exec(statement).first()
        if existing_link:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this organisation",
            )

        user_org_link = UserOrganisationLink(
            user_id=user_id, organisation_id=organisation_id, role=role
        )
        session.add(user_org_link)
        session.commit()
        session.refresh(user_org_link)

        return user_org_link
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


async def remove_member_from_organisation(
    session: Session, user_id: int, organisation_id: int
) -> None:
    try:
        user_org_link = session.get(UserOrganisationLink, (user_id, organisation_id))
        if not user_org_link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="UserOrganisationLink not found",
            )

        if user_org_link.role == UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the owner of the organisation",
            )

        session.delete(user_org_link)
        session.commit()
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )
