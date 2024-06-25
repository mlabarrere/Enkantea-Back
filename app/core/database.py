from app.core.config import settings
from contextlib import contextmanager
from sqlmodel import SQLModel, Session, create_engine

# Import all models
from app.models.clients import Client
from app.models.invoices import Invoice
from app.models.lots import Lot
from app.models.organisations import Organisation
from app.models.sales import Sale
from app.models.sellers import Seller
from app.models.users import User

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