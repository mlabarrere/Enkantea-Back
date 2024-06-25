from app.core.config import settings
from contextlib import contextmanager
from sqlmodel import SQLModel, Session, create_engine

# Import all models
from app.models.clients import Client  # noqa: F401
from app.models.invoices import Invoice  # noqa: F401
from app.models.lots import Lot  # noqa: F401
from app.models.organisations import Organisation  # noqa: F401
from app.models.sales import Sale  # noqa: F401
from app.models.sellers import Seller  # noqa: F401
from app.models.users import User  # noqa: F401

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