from sqlmodel import select
from app.models.users import User, UserCreate, UserRead, UserUpdate
from app.core.exceptions import DatabaseOperationError, UserNotFoundError
from app.core.database import get_db_session

def create_user(user_create: UserCreate) -> UserRead:
    """
    Create a new user in the database.

    Args:
        
        user_create (UserCreate): The user data to create.

    Returns:
        UserRead: The created user data.

    Raises:
        DatabaseOperationError: If an error occurs during user creation.
    """
    with get_db_session() as session:
        try:
            user_data = user_create.model_dump()
            db_user = User(**user_data)
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return UserRead.model_validate(db_user)
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(f"Failed to create user: {str(e)}")


def get_user_by_id(user_id: int) -> UserRead:
    """
    Retrieve a user by ID.

    Args:
        
        user_id (int): The ID of the user to retrieve.

    Returns:
        UserRead: The retrieved user data.

    Raises:
        UserNotFoundError: If the user is not found.
    """
    with get_db_session() as session:
        user = session.get(User, user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return UserRead.model_validate(user)


def get_user_by_email(email: str) -> UserRead:
    """
    Retrieve a user by email.

    Args:
        
        email (str): The email of the user to retrieve.

    Returns:
        UserRead: The retrieved user data.

    Raises:
        UserNotFoundError: If the user is not found.
    """
    with get_db_session() as session:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        if not user:
            raise UserNotFoundError(f"User with email {email} not found")
        return UserRead.model_validate(user)


def update_user(user_id: int, user_update: UserUpdate) -> UserRead:
    """
    Update an existing user in the database.

    Args:
        
        user_id (int): The ID of the user to update.
        user_update (UserUpdate): The updated user data.

    Returns:
        UserRead: The updated user data.

    Raises:
        UserNotFoundError: If the user is not found.
        DatabaseOperationError: If an error occurs during the update operation.
    """
    with get_db_session() as session:
        try:
            db_user = session.get(User, user_id)
            if not db_user:
                raise UserNotFoundError(f"User with id {user_id} not found")

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
            raise DatabaseOperationError(f"Failed to update user: {str(e)}")


def delete_user(user_id: int) -> UserRead:
    """
    Delete a user from the database.

    Args:
        
        user_id (int): The ID of the user to delete.

    Returns:
        UserRead: The deleted user data.

    Raises:
        UserNotFoundError: If the user is not found.
        DatabaseOperationError: If an error occurs during the delete operation.
    """
    with get_db_session() as session:
        try:
            db_user = session.get(User, user_id)
            if not db_user:
                raise UserNotFoundError(f"User with id {user_id} not found")

            deleted_user = UserRead.model_validate(db_user)
            session.delete(db_user)
            session.commit()
            return deleted_user
        except UserNotFoundError:
            raise
        except Exception as e:
            session.rollback()
            raise DatabaseOperationError(f"Failed to delete user: {str(e)}")


def get_users(skip: int = 0, limit: int = 100) -> list[UserRead]:
    """
    Retrieve a list of users.

    Args:
        
        skip (int): The number of users to skip (for pagination).
        limit (int): The maximum number of users to return.

    Returns:
        list[UserRead]: A list of retrieved users.

    Raises:
        DatabaseOperationError: If an error occurs during the retrieval operation.
    """
    with get_db_session() as session:
        try:
            statement = select(User).offset(skip).limit(limit)
            users = session.exec(statement).all()
            return [UserRead.model_validate(user) for user in users]
        except Exception as e:
            raise DatabaseOperationError(f"Failed to retrieve users: {str(e)}")


def get_users_by_organisation(
    organisation_id: int, skip: int = 0, limit: int = 100
) -> list[UserRead]:
    """
    Retrieve a list of users for a specific organisation.

    Args:
        
        organisation_id (int): The ID of the organisation.
        skip (int): The number of users to skip (for pagination).
        limit (int): The maximum number of users to return.

    Returns:
        list[UserRead]: A list of retrieved users for the specified organisation.

    Raises:
        DatabaseOperationError: If an error occurs during the retrieval operation.
    """
    with get_db_session() as session:
        try:
            statement = (
                select(User)
                .where(User.organisation_id == organisation_id)
                .offset(skip)
                .limit(limit)
            )
            users = session.exec(statement).all()
            return [UserRead.model_validate(user) for user in users]
        except Exception as e:
            raise DatabaseOperationError(
                f"Failed to retrieve users for organisation: {str(e)}"
            )
