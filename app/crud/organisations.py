from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.models.users import (
    Organisation,
    OrganisationCreate,
    OrganisationUpdate,
    OrganisationRead,
)


def create_organisation(
    *, session: Session, organisation_create: OrganisationCreate
) -> OrganisationRead:
    try:
        db_obj = Organisation.model_validate(organisation_create)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the organisation: {str(e)}",
        )


def update_organisation(
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


def get_organisation_by_id(
    *, session: Session, organisation_id: int
) -> OrganisationRead | None:
    try:
        organisation = session.get(Organisation, organisation_id)
        if not organisation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found"
            )
        return organisation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the organisation by ID: {str(e)}",
        )


def get_organisation_by_name(
    *, session: Session, company_name: str
) -> OrganisationRead | None:
    try:
        statement = select(Organisation).where(
            Organisation.company_name == company_name
        )
        organisation = session.exec(statement).first()
        if not organisation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found"
            )
        return organisation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the organisation by name: {str(e)}",
        )


def delete_organisation(
    *, session: Session, organisation_id: int
) -> OrganisationRead | None:
    try:
        db_organisation = session.get(Organisation, organisation_id)
        if not db_organisation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found"
            )
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
