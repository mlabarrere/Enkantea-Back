from app.core.config import settings
from contextlib import contextmanager
from sqlmodel import SQLModel, Session, create_engine

# Import all models
from app.clients.models import Client  # noqa: F401
from app.invoices.models import Invoice  # noqa: F401
from app.lots.models import Lot  # noqa: F401
from app.organisations.models_organisations import Organisation  # noqa: F401
from app.sales.models import Sale  # noqa: F401
from app.sellers.models import Seller  # noqa: F401
from app.users.models import User  # noqa: F401
from app.organisations.models_permissions import UserOrganisationLink  # noqa: F401
from app.inventories.models import Inventory  # noqa: F401

engine = create_engine(settings.DATABASE_URL)


def init_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_db_session():
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
