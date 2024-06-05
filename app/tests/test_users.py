import random
import string
import pytest
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from app.models.users import User, UserCreate, UserUpdate
from app.main import app
from app.crud.users import create_user, authenticate, get_user_by_email, update_user

# from app.core.security import verify_password

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=False)


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    #SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture():
    return TestClient(app)


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


user_data_tests = {
    "last_name": 'Pépito',#random_lower_string(),
    "first_name": random_lower_string(),
    "password": random_lower_string(),
    "email": 'pepito@gmail.com'# "email": random_email()
}


def test_create_user(session: Session) -> None:
    """
    Test de création d'un utilisateur
    """
    user_in = UserCreate(**user_data_tests)
    user = create_user(session=session, user_create=user_in)
    assert user.email == user_data_tests["email"]
    assert user.first_name == user_data_tests["first_name"]
    assert user.last_name == user_data_tests["last_name"]
    assert hasattr(user, "password")


def test_authenticate_user(session: Session) -> None:
    """
    Test d'authentification d'un utilisateur
    """
    authenticated_user = authenticate(
        session=session,
        email=user_data_tests["email"],
        password=user_data_tests["password"],
    )
    assert authenticated_user
    assert user_data_tests["email"] == authenticated_user.email


def test_unkonown_user(session: Session) -> None:
    """
    Test d'authentification d'un utilisateur
    """
    email = random_email()
    password = random_lower_string()
    with pytest.raises(HTTPException) as excinfo:
        authenticate(session=session, email=email, password=password)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND


def test_bad_password(session: Session) -> None:
    """
    Test d'authentification d'un utilisateur
    """
    with pytest.raises(HTTPException) as excinfo:
        _ = authenticate(
            session=session,
            email=user_data_tests["email"],
            password=random_lower_string(),
        )
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_user_by_email(session: Session) -> None:
    """
    Test de récupération d'un utilisateur par son email
    """
    fetched_user = get_user_by_email(session=session, email=user_data_tests["email"])
    assert fetched_user
    assert fetched_user.email == user_data_tests["email"]


def test_get_user_by_email_not_found(session: Session) -> None:
    """
    Test de récupération d'un utilisateur par son email
    """
    email = random_email()
    with pytest.raises(HTTPException) as excinfo:
        get_user_by_email(session=session, email=email)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in excinfo.value.detail


def test_get_user(session: Session) -> None:
    """
    Test de récupération d'un utilisateur
    """
    password = random_lower_string()
    email = random_email()
    user_in = UserCreate(
        email=email, password=password, last_name=random_lower_string(), first_name=random_lower_string()
    )
    user = create_user(session=session, user_create=user_in)
    user_2 = session.get(User, user.id)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_update_user(session: Session) -> None:
    """
    Test de mise à jour d'un utilisateur
    TODO : faire l'update de mots de passes
    """
    # Set User

    user = get_user_by_email(session=session, email=user_data_tests["email"])
    assert user
    assert user.email == user_data_tests["email"]

    # Set new Password
    new_last_name = "tata"  # random_lower_string()

    user_in_update = UserUpdate(last_name=new_last_name, is_superuser=True)
    if user.id is not None:
        _ = update_user(session=session, db_user=user, user_in=user_in_update)

    # Check if user is updated
    user_2 = session.get(User, user.id)
    assert user_2
    assert user.id == user_2.id
    assert user.email == user_2.email
    assert user.password == user_2.password
    assert user.last_name == new_last_name

    # assert verify_password(plain_password=new_password, hashed_password=user_2.password)
