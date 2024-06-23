import pytest
from pytest_postgresql import factories
from sqlmodel import SQLModel, create_engine, Session

# Import everything
from app.models.lots import Lot  # noqa: F401
from app.models.users import User  # noqa: F401
from app.models.clients import Client  # noqa: F401
from app.models.organisations import Organisation  # noqa: F401
from app.models.sales import Sale  # noqa: F401
from app.models.invoices import Invoice  # noqa: F401
from app.models.sellers import Seller  # noqa: F401


def load_database(**kwargs):
    connection_string = f"postgresql+psycopg2://{kwargs['user']}:@{kwargs['host']}:{kwargs['port']}/{kwargs['dbname']}"
    engine = create_engine(connection_string)
    SQLModel.metadata.create_all(engine)


postgresql_proc = factories.postgresql_proc(load=[load_database])
postgresql = factories.postgresql("postgresql_proc")


@pytest.fixture
def db_session(postgresql):
    connection_string = f"postgresql+psycopg2://{postgresql.info.user}:@{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}"
    engine = create_engine(connection_string)

    with Session(engine) as session:
        yield session
