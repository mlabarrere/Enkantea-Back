import pytest
from sqlmodel import Session, create_engine, SQLModel, select
from app.models.organisations import Organisation, OrganisationCreate
from app.models.users import User, UserCreate, UserRole
from app.models.sellers import Seller, SellerCreate
from app.models.clients import Client, ClientCreate
from app.models.lots import Lot, LotCreate
from app.models.sales import Sale, SaleCreate
from app.models.invoices import Invoice, InvoiceCreate

from app.service_layer.users import new_user
from app.service_layer.sellers import new_seller

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=True)

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

def test_sale_scenario(session: Session) -> None:
    # Step 1: Create user and organisation
    user_data = {"email": "user@example.com", "password": "password", "first_name": "John", "last_name": "Doe"}
    user = new_user(user_to_create=user_data)
    
    # TODO : Changer l'organsiation unique pour plusieurs orgas
    organisation = user.organisation
    
    # TODO : On suppose que l'étape de validation que l'usager peut agir au nom de l'organisation est validé
    
    # Step 2: Create a Seller in the organisation
    if user in 
    seller_data = {
        "first_name": "Seller",
        "last_name": "Test",
        "organisation_id": organisation.id
        }
    seller_create = SellerCreate(**seller_data)
    seller = new_seller(seller_create=seller_create)

    # Step 3: Create a Client (Buyer) in the organisation
    client_data = {"first_name": "Client", "last_name": "Buyer", "organisation_id": organisation.id}
    client_create = ClientCreate(**client_data)
    client = create_client(session=session, user_id=user.id, client_create=client_create)

    # Step 4: Create a Lot in the organisation
    lot_data = {"name": "Test Lot", "description": "Test Description", "starting_bid": 100.0, "organisation_id": organisation.id, "seller_id": seller.id}
    lot_create = LotCreate(**lot_data)
    lot = create_lot(session=session, user_id=user.id, lot_create=lot_create)

    # Step 5: Create a Sale in the organisation
    sale_data = {"title": "Test Sale", "organisation_id": organisation.id}
    sale_create = SaleCreate(**sale_data)
    sale = create_sale(session=session, sale_create=sale_create)

    # Step 6: Add the lot to the sale at a given price
    lot_update_data = {"sale_id": sale.id}
    lot_update = LotUpdate(**lot_update_data)
    updated_lot = update_lot(session=session, user_id=user.id, lot_id=lot.id, lot_update=lot_update)

    # Step 7: Sell the lot at a hammer price
    hammer_price = 200.0
    lot_update_data = {"hammer_price": hammer_price, "buyer_id": client.id}
    lot_update = LotUpdate(**lot_update_data)
    sold_lot = update_lot(session=session, user_id=user.id, lot_id=updated_lot.id, lot_update=lot_update)

    # Step 8: Generate an invoice for the buyer
    invoice_data = {"sale_id": sale.id, "number": "INV-001", "client_id": client.id, "organisation_id": organisation.id}
    invoice_create = InvoiceCreate(**invoice_data)
    invoice = create_invoice(session=session, invoice_create=invoice_create)

    # Assertions to check if everything is set up correctly
    assert lot.name == "Test Lot"
    assert lot.seller_id == seller.id
    assert lot.sale_id == sale.id
    assert sold_lot.hammer_price == hammer_price
    assert sold_lot.buyer_id == client.id
    assert invoice.sale_id == sale.id
    assert invoice.client_id == client.id
    assert invoice.number == "INV-001"
