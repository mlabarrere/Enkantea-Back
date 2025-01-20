import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from jose import jwt
from uuid import UUID

from app.main import app
from app.core.config import settings
from app.organisations.models_permissions import Role
from app.core.exceptions import TokenError
from app.auth.CRUD import (
    decode_access_token,
    decode_refresh_token,
    create_access_token,
    create_refresh_token,
)
from app.auth.models import PublicAccessTokenPayload, RefreshTokenPayload

client = TestClient(app=app, root_path=settings.API_V1_STR)


@pytest.fixture
def create_user():
    def _create_user(email):
        user_data = {
            "email": email,
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
        }
        response = client.post("/users/new", json=user_data)
        assert response.status_code == 201
        return user_data

    return _create_user


def login_user(email, password):
    login_data = {"username": email, "password": password}
    response = client.post("/auth/login/", data=login_data)
    assert response.status_code == 200
    return response.json()


FOLDER_PATH = "/auth"

client = TestClient(app)
client.base_url = str(client.base_url) + settings.API_V1_STR
client.base_url = str(client.base_url).rstrip("/") + "/"


def test_read_main():
    response = client.get(url="/auth")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello Auth"}


def test_create_user_and_login():
    # 1. Création d'un nouvel utilisateur
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "User",
    }
    response = client.post("/users/new", json=user_data)
    assert response.status_code == 201

    # Connexion avec les credentials
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    response = client.post("/auth/login/", data=login_data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens


def test_create_and_decode_access_token():
    payload = PublicAccessTokenPayload(
        user_uuid="123e4567-e89b-12d3-a456-426614174000",
        orga_uuids=["123e4567-e89b-12d3-a456-426614174001"],
        role=Role.OWNER.value,
    )
    token = create_access_token(payload)
    decoded = decode_access_token(token)

    assert str(decoded.user_uuid) == payload.user_uuid
    assert [str(uuid) for uuid in decoded.orga_uuids] == payload.orga_uuids
    assert decoded.role == Role.OWNER


async def test_create_and_decode_refresh_token():
    user_uuid = UUID("123e4567-e89b-12d3-a456-426614174000")
    token = await create_refresh_token(user_uuid)
    decoded = decode_refresh_token(token)

    assert UUID(decoded.user_uuid) == user_uuid
    assert decoded.exp > datetime.now(timezone.utc)


def test_token_validity_and_association(create_user):
    # Créer deux utilisateurs
    user1 = create_user("user1@example.com")
    user2 = create_user("user2@example.com")

    # Connecter les deux utilisateurs et obtenir leurs tokens
    tokens1 = login_user(user1["email"], user1["password"])
    tokens2 = login_user(user2["email"], user2["password"])

    access_token1 = tokens1["access_token"]
    access_token2 = tokens2["access_token"]

    # Vérifier que les tokens sont différents
    assert access_token1 != access_token2

    # Décoder et vérifier le contenu des tokens
    payload1 = decode_access_token(access_token1)
    payload2 = decode_access_token(access_token2)

    # Vérifier que chaque token contient les bonnes informations
    assert payload1.user_uuid != payload2.user_uuid
    assert payload1.orga_uuids and payload2.orga_uuids
    assert payload1.role and payload2.role

    # Vérifier que les tokens sont associés aux bons utilisateurs
    headers1 = {"Authorization": f"Bearer {access_token1}"}
    headers2 = {"Authorization": f"Bearer {access_token2}"}

    response1 = client.get("/users/me", headers=headers1)
    response2 = client.get("/users/me", headers=headers2)

    assert response1.status_code == 200
    assert response2.status_code == 200

    user_info1 = response1.json()
    user_info2 = response2.json()

    assert user_info1["email"] == user1["email"]
    assert user_info2["email"] == user2["email"]

    # Tester qu'un token ne peut pas être utilisé pour un autre utilisateur
    response_cross = client.get("/users/me", headers=headers1)
    assert response_cross.status_code == 200
    assert response_cross.json()["email"] != user2["email"]

    # Vérifier que les tokens expirés sont rejetés
    expired_payload = PublicAccessTokenPayload(
        user_uuid=str(payload1.user_uuid),
        orga_uuids=[str(uuid) for uuid in payload1.orga_uuids],
        role=payload1.role.value,
        exp=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    expired_token = create_access_token(expired_payload)
    with pytest.raises(TokenError):
        decode_access_token(expired_token)


def test_refresh_token_workflow(create_user):
    # Créer un utilisateur et se connecter
    user = create_user("refresh_test@example.com")
    tokens = login_user(user["email"], user["password"])

    assert "access_token" in tokens
    assert "refresh_token" in tokens

    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # Vérifier que le refresh token est généré
    assert refresh_token is not None

    # Décoder et vérifier le contenu du refresh token
    refresh_payload = decode_refresh_token(token=refresh_token)
    access_payload = decode_access_token(token=access_token)
    assert UUID(refresh_payload.user_uuid) == access_payload.user_uuid

    # Utiliser l'access token normalement
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200

    # Simuler un access token expiré
    expired_access_token_payload = PublicAccessTokenPayload(
        user_uuid=str(access_payload.user_uuid),
        orga_uuids=[],  # Vous pouvez ajouter des orga_uuids si nécessaire
        role=Role.OWNER.value,
    )
    expired_access_token_payload.exp = datetime.now(timezone.utc) - timedelta(minutes=1)
    expired_access_token = create_access_token(expired_access_token_payload)

    # Utiliser l'access token expiré
    headers_expired = {"Authorization": f"Bearer {expired_access_token}"}
    with pytest.raises(TokenError):
        decode_access_token(token=expired_access_token)

    # Utiliser le refresh token pour obtenir un nouveau access token
    refresh_data = {"refresh_token": refresh_token}
    response = client.post("/auth/refresh", headers=refresh_data)
    assert response.status_code == 200
    new_tokens = response.json()
    assert "access_token" in new_tokens

    # Vérifier la validité du nouveau token
    new_payload = decode_access_token(new_tokens["access_token"])
    assert str(new_payload.user_uuid) == user["uuid"]

    # Utiliser le nouveau access token
    new_headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
    response = client.get("/users/me", headers=new_headers)
    assert response.status_code == 200

    # Tester avec un refresh token modifié
    modified_refresh_token = refresh_token[:-1] + "X"
    with pytest.raises(TokenError):
        decode_refresh_token(modified_refresh_token)

    # Tester avec un refresh token expiré
    expired_refresh_payload = RefreshTokenPayload(
        user_uuid=str(UUID(user["uuid"])),
        exp=datetime.now(timezone.utc) - timedelta(days=1),
    )
    expired_refresh_token = jwt.encode(
        expired_refresh_payload.model_dump(),
        settings.REFRESH_TOKEN_SECRET,
        algorithm=settings.TOKEN_ALGORITHM,
    )
    with pytest.raises(TokenError):
        decode_refresh_token(expired_refresh_token)


"""
def test_token_validity_and_association(create_user):
    # Créer deux utilisateurs
    user1 = create_user("user1@example.com")
    user2 = create_user("user2@example.com")

    # Connecter les deux utilisateurs et obtenir leurs tokens
    tokens1 = login_user(user1["email"], user1["password"])
    tokens2 = login_user(user2["email"], user2["password"])

    access_token1 = tokens1["access_token"]
    access_token2 = tokens2["access_token"]

    # Vérifier que les tokens sont différents
    assert access_token1 != access_token2

    # Décoder et vérifier le contenu des tokens
    payload1 = decode_access_token(access_token1)
    payload2 = decode_access_token(access_token2)

    # Vérifier que chaque token contient les bonnes informations
    assert payload1.user_uuid != payload2.user_uuid
    assert payload1.orga_uuids and payload2.orga_uuids
    assert payload1.role and payload2.role
    # assert payload1["iss"] == settings.DOMAIN
    # assert payload2["iss"] == settings.DOMAIN

    # Vérifier que les tokens sont associés aux bons utilisateurs
    headers1 = {"Authorization": f"Bearer {access_token1}"}
    headers2 = {"Authorization": f"Bearer {access_token2}"}

    response1 = client.get("/users/me", headers=headers1)
    response2 = client.get("/users/me", headers=headers2)

    assert response1.status_code == 200
    assert response2.status_code == 200

    user_info1 = response1.json()
    user_info2 = response2.json()

    assert user_info1["email"] == user1["email"]
    assert user_info2["email"] == user2["email"]

    # Tester qu'un token ne peut pas être utilisé pour un autre utilisateur
    response_cross = client.get(
        "/users/me", headers={"Authorization": f"Bearer {access_token1}"}
    )
    assert response_cross.status_code == 200
    assert response_cross.json()["email"] != user2["email"]

    # Vérifier que les tokens invalides sont rejetés
    invalid_token = access_token1[:-1] + "X"  # Modifier le dernier caractère
    with pytest.raises(TokenError):
        _ = client.get(
            "/users/me", headers={"Authorization": f"Bearer {invalid_token}"}
        )

    # Vérifier que les tokens expirés sont rejetés (simulation)
    expired_payload = payload1.copy()
    expired_payload["exp"] = 1  # Timestamp dans le passé
    expired_token = jwt.encode(
        expired_payload, settings.TOKEN_SECRET, algorithm=settings.TOKEN_ALGORITHM
    )
    with pytest.raises(TokenError):
        _ = client.get(
            "/users/me", headers={"Authorization": f"Bearer {expired_token}"}
        )

    # Vérifier que les tokens avec des rôles modifiés sont rejetés
    modified_payload = payload1.copy()
    modified_payload["role"] = (
        Role.OWNER if payload1["role"] != Role.OWNER.value else Role.VIEWER
    )
    # Pas bon
    # with pytest.raises(TokenError):
    #    _ = client.get(
    #        "/users/me", headers={"Authorization": f"Bearer {modified_payload}"}
    #    )

def test_refresh_token_workflow(create_user):
    # Créer un utilisateur et se connecter
    user = create_user("refresh_test@example.com")
    tokens = login_user(user["email"], user["password"])

    assert "access_token" in tokens
    assert "refresh_token" in tokens

    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # Vérifier que le refresh token est généré
    assert refresh_token is not None

    # Utiliser l'access token normalement
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200

    # Simuler un access token expiré
    expired_payload = decode_access_token(access_token)
    expired_payload.exp = datetime.now(timezone.utc) - timedelta(minutes=1)
    expired_token = jwt.encode(
        expired_payload, settings.TOKEN_SECRET, algorithm=settings.TOKEN_ALGORITHM
    )

    # Utiliser l'access token expiré
    headers_expired = {"Authorization": f"Bearer {expired_token}"}
    with pytest.raises(TokenError):
        _ = client.get("/users/me", headers=headers_expired)

    # Utiliser le refresh token pour obtenir un nouveau access token
    refresh_data = {"refresh_token": refresh_token}
    response = client.post("/auth/refresh", json=refresh_data)
    assert response.status_code == 200
    new_tokens = response.json()
    assert "access_token" in new_tokens

    # Vérifier la qualité du nouveau token
    new_payload = jwt.decode(
        new_tokens['access_token'],
        settings.TOKEN_SECRET,
        algorithms=[settings.TOKEN_ALGORITHM]
    )
    assert new_payload['user_uuid'] == user['email']

    # Utiliser le nouveau access token
    new_headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
    response = client.get("/users/me", headers=new_headers)
    assert response.status_code == 200

    # Tester avec un refresh token modifié
    modified_refresh_token = refresh_token[:-1] + "X"
    modified_refresh_data = {"refresh_token": modified_refresh_token}
    with pytest.raises(TokenError):
        _ = client.post("/auth/refresh", json=modified_refresh_data)

    # Tester avec un refresh token expiré
    expired_refresh_payload = jwt.decode(
        refresh_token,
        settings.REFRESH_TOKEN_SECRET,
        algorithms=[settings.TOKEN_ALGORITHM],
        options={"verify_signature": False},
    )
    expired_refresh_payload["exp"] = datetime.now(timezone.utc) - timedelta(days=1)
    expired_refresh_token = jwt.encode(
        expired_refresh_payload, settings.REFRESH_TOKEN_SECRET, algorithm=settings.TOKEN_ALGORITHM
    )
    expired_refresh_data = {"refresh_token": expired_refresh_token}
    with pytest.raises(TokenError):
        _ = client.post("/auth/refresh", json=expired_refresh_data)

"""
"""def test_access_token_expiration_and_refresh(create_user):
    # Créer un utilisateur et se connecter
    user = create_user("expiration_test@example.com")
    tokens = login_user(user["email"], user["password"])

    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # Simuler un access token expiré
    expired_payload = jwt.decode(
        access_token,
        settings.TOKEN_SECRET,
        algorithms=[settings.TOKEN_ALGORITHM],
        options={"verify_signature": False},
    )
    expired_payload["exp"] = datetime.utcnow() - timedelta(minutes=1)
    expired_token = jwt.encode(
        expired_payload, settings.TOKEN_SECRET, algorithm=settings.TOKEN_ALGORITHM
    )

    # Tenter d'utiliser l'access token expiré
    headers_expired = {"Authorization": f"Bearer {expired_token}"}
    with pytest.raises(TokenError):
        client.get("/users/me", headers=headers_expired)

    # Utiliser le refresh token pour obtenir un nouveau access token
    refresh_data = {"refresh_token": refresh_token}
    response = client.post("/auth/refresh", json=refresh_data)
    assert response.status_code == 200
    new_tokens = response.json()
    assert "access_token" in new_tokens

    # Utiliser le nouveau access token
    new_headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
    response = client.get("/users/me", headers=new_headers)
    assert response.status_code == 200

def test_refresh_token_reuse(create_user):
    # Créer un utilisateur et se connecter
    user = create_user("reuse_test@example.com")
    tokens = login_user(user["email"], user["password"])

    refresh_token = tokens["refresh_token"]

    # Utiliser le refresh token une première fois
    refresh_data = {"refresh_token": refresh_token}
    response = client.post("/auth/refresh", json=refresh_data)
    assert response.status_code == 200

    # Tenter de réutiliser le même refresh token
    response = client.post("/auth/refresh", json=refresh_data)
    assert response.status_code == 401  # Le token devrait être invalidé
"""
