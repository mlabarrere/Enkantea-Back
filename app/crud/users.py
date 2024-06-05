from sqlmodel import select, Session
from fastapi import HTTPException, status
from app.models import User, UserCreate, UserUpdate, UserRead
from app.core.security import get_password_hash, verify_password


def create_user(*, session: Session, user_create: UserCreate) -> UserRead:
    db_obj = User.model_validate(
        obj=user_create, update={"password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> UserRead:
    user_data = user_in.model_dump(exclude_unset=True)
    if "password" in user_data:
        user_data["password"] = get_password_hash(user_data["password"])
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> UserRead | None:
    try:
        statement = select(User).where(User.email == email)
        session_user = session.exec(statement).first()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the user: {str(e)}",
        )
    if not session_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found.",
        )
    return session_user


def authenticate(session: Session, email: str, password: str) -> UserRead | None:
    try:
        db_user = get_user_by_email(session=session, email=email)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        ) from e
    if not db_user or not verify_password(
        plain_password=password, hashed_password=db_user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    return db_user
