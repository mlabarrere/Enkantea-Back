import random
import string
import pytest
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from app.models import User, UserCreate, UserUpdate
from app.main import app
from app.crud.users import create_user, authenticate, get_user_by_email, update_user
# from app.core.security import verify_password

# Configuration de la base de données pour les tests
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=False)


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


@pytest.fixture(name="session")
def session_fixture():
    # Créer les tables
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    # Supprimer les tables après le test
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture():
    return TestClient(app)


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def test_create_user(session: Session) -> None:
    """""
    Test de création d'un utilisateur
    """
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=session, user_create=user_in)
    assert user.email == email
    assert hasattr(user, "password")


def test_authenticate_user(session: Session) -> None:
    """
    Test d'authentification d'un utilisateur
    """
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=session, user_create=user_in)
    authenticated_user = authenticate(
        session=session, email=email, password=password
    )
    assert authenticated_user
    assert user.email == authenticated_user.email


def test_not_authenticate_user(session: Session) -> None:
    """
    Test d'authentification d'un utilisateur
    """
    email = random_email()
    password = random_lower_string()
    with pytest.raises(HTTPException) as excinfo:
        authenticate(session=session, email=email, password=password)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid credentials" in excinfo.value.detail


def test_check_if_user_is_active(session: Session) -> None:
    """
    Test de vérification de l'état d'un utilisateur
    """
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=session, user_create=user_in)
    assert user.is_active is True


def test_check_if_user_is_active_inactive(session: Session) -> None:
    """
    Test de vérification de l'état d'un utilisateur
    """
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_active=False)
    user = create_user(session=session, user_create=user_in)
    assert user.is_active is False


def test_check_if_user_is_superuser(session: Session) -> None:
    """
    Test de vérification de l'état d'un utilisateur
    """
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = create_user(session=session, user_create=user_in)
    assert user.is_superuser is True


def test_check_if_user_is_superuser_normal_user(session: Session) -> None:
    """
    Test de vérification de l'état d'un utilisateur
    """
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=session, user_create=user_in)
    assert user.is_superuser is False


def test_get_user_by_email(session: Session) -> None:
    """
    Test de récupération d'un utilisateur par son email
    """
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    created_user = create_user(session=session, user_create=user_in)

    fetched_user = get_user_by_email(session=session, email=email)
    assert fetched_user
    assert fetched_user.email == created_user.email


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
    user_in = UserCreate(email=email, password=password, is_superuser=True)
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
    user_data = {
        "last_name": random_lower_string(),
        "first_name": random_lower_string(),
        "password": random_lower_string(),
        "email": random_email(),
    }
    user_in = UserCreate(**user_data)
    user = create_user(session=session, user_create=user_in)

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
