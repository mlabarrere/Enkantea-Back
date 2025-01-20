from datetime import datetime
from app.organisations.CRUD_permissions import add_or_update_user_role_organisation_link
from app.organisations.CRUD import get_members_from_organisation
from app.organisations.models_permissions import UserOrganisationLink, UserRole
from app.users.models import UserRead
from uuid import UUID


async def add_user_to_organisation(
    user_uuid: UUID, orga_uuid: UUID, role: UserRole
) -> UserOrganisationLink | None:
    """
    Ajoute un utilisateur à une organisation avec un rôle spécifique.
    """
    # Création du modèle UserOrganisationLink
    user_org_link = UserOrganisationLink(
        user_uuid=user_uuid,
        orga_uuid=orga_uuid,
        role=role,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    return await add_or_update_user_role_organisation_link(user_org_link)


async def get_users_from_organisation(orga_uuid: UUID) -> list[UserRead]:
    """
    Récupère la liste des utilisateurs d'une organisation.
    """
    return await get_members_from_organisation(orga_uuid)


async def get_role_from_organisation(
    user_uuid: UUID, orga_uuid: UUID
) -> UserOrganisationLink:
    """
    Récupère le rôle d'un utilisateur dans une organisation.
    """
    return await UserOrganisationLink.get(user_uuid=user_uuid, orga_uuid=orga_uuid)
