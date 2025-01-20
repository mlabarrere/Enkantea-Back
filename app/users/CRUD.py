from uuid import UUID
from sqlmodel import select, Session
from app.core.config import settings
from app.core.exceptions import DatabaseOperationError, UserNotFoundError
from app.core.database import get_db_session
from app.users.models import User, UserCreate, UserRead, UserUpdate, UserRegister
from app.organisations.models_permissions import UserOrganisationLink


def _get_password_hash(password: str) -> str:
    return settings.pwd_context.hash(secret=password)


def _get_user(session: Session, user_uuid: UUID) -> User:
    user = session.get(User, user_uuid)
    if not user:
        raise UserNotFoundError(f"User with id {user_uuid} not found")
    return user


async def create_user(user_create: UserCreate) -> UserRead:
    with get_db_session() as session:
        try:
            db_user = User(**user_create.model_dump())
            db_user.password = _get_password_hash(db_user.password)
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return UserRead.model_validate(db_user)
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(f"Failed to create user: {e}")


async def get_user_by_uuid(user_uuid: UUID) -> UserRead:
    with get_db_session() as session:
        user = _get_user(session, user_uuid)
        return UserRead.model_validate(user)


async def get_user_by_email(email: str) -> UserRegister:
    with get_db_session() as session:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        if not user:
            raise UserNotFoundError(f"User with email {email} not found")
        return UserRegister(uuid=user.uuid, password=user.password)


async def update_user(user_update: UserUpdate) -> UserRead:
    with get_db_session() as session:
        try:
            db_user = _get_user(session, user_update.uuid)
            user_data = user_update.model_dump(exclude_unset=True)
            for key, value in user_data.items():
                setattr(db_user, key, value)
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return UserRead.model_validate(db_user)
        except UserNotFoundError:
            raise
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(f"Failed to update user: {e}")


async def delete_user(user_uuid: UUID) -> UserRead:
    with get_db_session() as session:
        try:
            db_user = _get_user(session, user_uuid)
            deleted_user = UserRead.model_validate(db_user)
            session.delete(db_user)
            session.commit()
            return deleted_user
        except UserNotFoundError:
            raise
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(f"Failed to delete user: {e}")


async def get_all_orgas_of_user(user_uuid: UUID) -> list[UUID]:
    with get_db_session() as session:
        try:
            statement = select(UserOrganisationLink.orga_uuid).where(
                UserOrganisationLink.user_uuid == user_uuid
            )
            return list(session.exec(statement).unique())
        except Exception as e:
            raise DatabaseOperationError(f"Failed to retrieve organisations ID: {e}")
