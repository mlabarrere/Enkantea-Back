from sqlmodel import select, Session
from fastapi import HTTPException, status
from app.models.users import User, UserCreate, UserUpdate, UserRead
from app.models.users import Organisation, OrganisationCreate, UserOrganisationLink, UserRole
from app.core.security import get_password_hash, verify_password


def create_user(*, session: Session, user_create: UserCreate) -> UserRead:
    try:
        # Créer l'organisation
        organisation_create = OrganisationCreate(company_name=f'{user_create.first_name} {user_create.last_name}')
        organisation = Organisation.model_validate(obj=organisation_create)
        session.add(organisation)
        session.commit()
        session.refresh(organisation)

        # Créer l'utilisateur
        db_user = User.model_validate(obj=user_create)
        db_user.organisation_id = organisation.id
        db_user.password = get_password_hash(user_create.password)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        # Lier l'utilisateur à l'organisation avec le rôle OWNER
        user_org_link = UserOrganisationLink(user_id=db_user.id, organisation_id=organisation.id, role=UserRole.OWNER)
        session.add(user_org_link)
        session.commit()
        session.refresh(user_org_link)

        return db_user
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'An error occurred while creating the user and organisation: {str(e)}'
        )



def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> UserRead:
    try:
        user_data = user_in.model_dump(exclude_unset=True)
        if 'password' in user_data.keys():
            raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='Password cannot be updated',
                    )
        for key, value in user_data.items():
            setattr(db_user, key, value)

        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'An error occurred while updating the user: {str(e)}',
        )


def get_user_by_email(*, session: Session, email: str) -> UserRead | None:
    try:
        statement = select(User).where(User.email == email)
        session_user = session.exec(statement).first()
        if not session_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'User with email {email} not found.',
            )
        return session_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'An error occurred while fetching the user: {str(e)}',
        )


def authenticate(session: Session, email: str, password: str) -> UserRead | None:
    try:
        db_user = get_user_by_email(session=session, email=email)
        if not db_user or not verify_password(
            plain_password=password, hashed_password=db_user.password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid password'
            )
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error occurred',
        ) from e

