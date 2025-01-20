import pytest
from app.core.config import settings
from app.core.database import init_db, get_db_session


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.ENVIRONMENT = "tests"


@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()  # Initialise la base de données pour les tests
    yield
    # Nettoyage après chaque test
    with get_db_session() as session:
        session.close()
    init_db()  # Réinitialise la base de données pour le prochain test


@pytest.fixture
def db_session():
    with get_db_session() as session:
        yield session
