"""
TODO : 
Création de lot
- Création réussie avec tous les champs requis
- Tentative de création sans authentification
- Tentative de création avec des données invalides
- Création avec des champs optionnels


Récupération de lot
- Récupération d'un lot spécifique par ID
- Récupération de tous les lots d'un utilisateur
- Tentative de récupération d'un lot inexistant
- Tentative de récupération d'un lot appartenant à un autre utilisateur


Mise à jour de lot
- Mise à jour réussie de tous les champs modifiables
- Mise à jour partielle (seulement certains champs)
- Tentative de mise à jour d'un lot inexistant
- Tentative de mise à jour d'un lot appartenant à un autre utilisateur
- Tentative de mise à jour avec des données invalides


Suppression de lot
- Suppression réussie d'un lot
- Tentative de suppression d'un lot inexistant
- Tentative de suppression d'un lot appartenant à un autre utilisateur


Autorisation et authentification
- Accès aux routes avec un token valide
- Accès aux routes avec un token expiré
- Accès aux routes sans token
- Accès aux routes avec un token invalide


Gestion des erreurs
- Réponses appropriées pour chaque type d'erreur (400, 401, 403, 404, 500)
- Messages d'erreur clairs et informatifs


Performances
- Temps de réponse pour chaque opération CRUD
- Comportement sous charge (plusieurs requêtes simultanées)


Validations des données
- Respect des contraintes de champs (longueur, type, format)
- Gestion des valeurs nulles ou vides pour les champs obligatoires


Intégration avec d'autres entités
- Liens corrects avec l'organisation associée
- Comportement lors de la suppression d'une organisation liée


Pagination et filtrage (si implémentés)
- Fonctionnement correct de la pagination pour la liste des lots
- Application correcte des filtres sur la liste des lots


Journalisation et audit
- Enregistrement correct des actions de création, mise à jour et suppression
- Traçabilité des modifications


Gestion des transactions
- Rollback correct en cas d'erreur lors de la création ou mise à jour

"""

import pytest
from sqlmodel import Session, create_engine, SQLModel, select
from fastapi import HTTPException, status
from datetime import datetime
from app.models.users import User, UserCreate, UserRole, UserOrganisationLink
from app.models.clients import Client, ClientCreate
from app.models.lots import Lot, LotCreate, LotUpdate
from app.models.organisations import Organisation, OrganisationCreate
from app.data_layer.users import create_user, add_user_to_organisation
from app.data_layer.clients import create_client
from app.data_layer.lots import create_lot, get_lot_by_id, update_lot, delete_lot
from app.data_layer.organisations import create_organisation

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=False)


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


def test_create_user_with_organisation(session: Session) -> None:
    user_data = {
        "email": "user@example.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe",
    }
    user_create = UserCreate(**user_data)
    user = create_user(session=session, user_create=user_create)

    # Vérification de la création de l'utilisateur
    assert user.email == user_data["email"]
    assert user.first_name == user_data["first_name"]
    assert user.last_name == user_data["last_name"]

    # Vérification de la création de l'organisation via la relation utilisateur
    assert user.organisation is not None
    organisation = user.organisation
    organisation_name = f"{user_data['first_name']} {user_data['last_name']}"
    assert organisation.company_name == organisation_name

    # Vérification du lien entre l'utilisateur et l'organisation
    user_org_link = session.exec(
        select(UserOrganisationLink).where(
            UserOrganisationLink.user_id == user.id,
            UserOrganisationLink.organisation_id == organisation.id,
        )
    ).first()
    assert user_org_link is not None
    assert user_org_link.role == UserRole.OWNER


def test_create_lot_with_organisation(session: Session) -> None:
    user_data = {
        "email": "user@example.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe",
    }
    user_create = UserCreate(**user_data)
    user = create_user(session=session, user_create=user_create)

    # Accès à l'organisation via l'utilisateur
    organisation = user.organisation

    client_data = {
        "first_name": "Client",
        "last_name": "Test",
        "organisation_id": organisation.id,
    }
    client_create = ClientCreate(**client_data)
    client = create_client(
        session=session, user_id=user.id, client_create=client_create
    )

    lot_data = {
        "name": "Test Lot",
        "description": "Test Description",
        "starting_bid": 100.0,
        "organisation_id": organisation.id,
        "seller_id": client.id,
    }
    lot_create = LotCreate(**lot_data)
    lot = create_lot(session=session, user_id=user.id, lot_create=lot_create)

    # Vérification de la création du lot
    assert lot.name == lot_data["name"]
    assert lot.description == lot_data["description"]
    assert lot.organisation_id == organisation.id


def test_create_lot_in_different_organisations(session: Session) -> None:
    # Création de l'utilisateur et de la première organisation
    user_data = {
        "email": "user@example.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe",
    }
    user_create = UserCreate(**user_data)
    user = create_user(session=session, user_create=user_create)

    # Création de la deuxième organisation
    organisation_data = {"company_name": "Second Organisation"}
    organisation_create = OrganisationCreate(**organisation_data)
    organisation2 = create_organisation(
        session=session, organisation_create=organisation_create
    )
    add_user_to_organisation(
        session=session,
        user_id=user.id,
        organisation_id=organisation2.id,
        role=UserRole.ADMIN,
    )

    # Création d'un client dans la deuxième organisation
    client_data = {
        "first_name": "Client",
        "last_name": "Test",
        "organisation_id": organisation2.id,
    }
    client_create = ClientCreate(**client_data)
    client = create_client(
        session=session, user_id=user.id, client_create=client_create
    )

    # Création d'un lot dans la deuxième organisation
    lot_data = {
        "name": "Test Lot",
        "description": "Test Description",
        "starting_bid": 100.0,
        "organisation_id": organisation2.id,
        "seller_id": client.id,
    }
    lot_create = LotCreate(**lot_data)
    lot = create_lot(session=session, user_id=user.id, lot_create=lot_create)

    # Vérification de la création du lot dans la deuxième organisation
    assert lot.name == lot_data["name"]
    assert lot.description == lot_data["description"]
    assert lot.organisation_id == organisation2.id


def test_user_cannot_create_lot_in_unassigned_organisation(session: Session) -> None:
    
    # Etape 1 : Créer usager dans première organisation
    user_data = {
        "email": "user@example.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe",
    }
    user_create = UserCreate(**user_data)
    user = create_user(session=session, user_create=user_create)
    assert user.email == user_data["email"]
    assert user.organisation is not None
    assert user.organisation.company_name == f"{user_data['first_name']} {user_data['last_name']}"
    assert len(user.organisation.users)== 1
    assert len(user.organisation.clients) == 0
    assert len(user.organisation.lots) == 0

    # Etape 2 : Créer organisation sans ajouter d'utilisateur
    organisation_data = {"company_name": "Second Organisation"}
    organisation_create = OrganisationCreate(**organisation_data)
    organisation2 = create_organisation(
        session=session, organisation_create=organisation_create
    )
    assert organisation2.company_name == organisation_data["company_name"]
    assert len(organisation2.users) == 0
    assert len(organisation2.clients) == 0
    assert len(organisation2.lots) == 0
    assert user.organisation != organisation2

    # Etape 3 : Création d'un client dans la deuxième organisation avec l'user de l'autre orga 
    client_data = {
        "first_name": "Client",
        "last_name": "Test",
        "organisation_id": organisation2.id,
    }
    client_create = ClientCreate(**client_data)
    with pytest.raises(HTTPException) as excinfo:
        _ = create_client(
            session=session, user_id=user.id, client_create=client_create
        )
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN

    # Tentative de création d'un lot dans la deuxième organisation
    lot_data = {
        "name": "Test Lot",
        "description": "Test Description",
        "starting_bid": 100.0,
        "organisation_id": organisation2.id,
        "seller_id": 1,
    }
    lot_create = LotCreate(**lot_data)
    with pytest.raises(HTTPException) as excinfo:
        create_lot(session=session, user_id=user.id, lot_create=lot_create)

    # Vérification de l'exception
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN


def test_update_lot(session: Session) -> None:
    """
    Test updating a lot's details.
    """
    user_data = {
        "email": "user@example.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe",
    }
    user_create = UserCreate(**user_data)
    user = create_user(session=session, user_create=user_create)

    # Accès à l'organisation via l'utilisateur
    organisation = user.organisation

    client_data = {
        "first_name": "Client",
        "last_name": "Test",
        "organisation_id": organisation.id,
    }
    client_create = ClientCreate(**client_data)
    client = create_client(
        session=session, user_id=user.id, client_create=client_create
    )

    lot_data = {
        "name": "Test Lot",
        "description": "Test Description",
        "starting_bid": 100.0,
        "organisation_id": organisation.id,
        "seller_id": client.id,
    }
    lot_create = LotCreate(**lot_data)
    created_lot = create_lot(session=session, user_id=user.id, lot_create=lot_create)

    update_data = {"name": "Updated Lot", "description": "Updated Description"}
    lot_update = LotUpdate(**update_data)
    updated_lot = update_lot(
        session=session, user_id=user.id, lot_id=created_lot.id, lot_update=lot_update
    )

    # Vérification de la mise à jour du lot
    assert updated_lot.name == update_data["name"]
    assert updated_lot.description == update_data["description"]


def test_delete_lot(session: Session) -> None:
    """
    Test deleting a lot.
    """
    user_data = {
        "email": "user@example.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe",
    }
    user_create = UserCreate(**user_data)
    user = create_user(session=session, user_create=user_create)

    # Accès à l'organisation via l'utilisateur
    organisation = user.organisation

    client_data = {
        "first_name": "Client",
        "last_name": "Test",
        "organisation_id": organisation.id,
    }
    client_create = ClientCreate(**client_data)
    client = create_client(
        session=session, user_id=user.id, client_create=client_create
    )

    lot_data = {
        "name": "Test Lot",
        "description": "Test Description",
        "starting_bid": 100.0,
        "organisation_id": organisation.id,
        "seller_id": client.id,
    }
    lot_create = LotCreate(**lot_data)
    created_lot = create_lot(session=session, user_id=user.id, lot_create=lot_create)

    deleted_lot = delete_lot(session=session, user_id=user.id, lot_id=created_lot.id)

    # Vérification de la suppression du lot
    assert deleted_lot.id == created_lot.id
    with pytest.raises(HTTPException) as excinfo:
        get_lot_by_id(session=session, user_id=user.id, lot_id=created_lot.id)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
