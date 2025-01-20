# app/crud/roles_permissions.py
from sqlmodel import select
from app.core.database import get_db_session
from app.organisations.models_permissions import UserOrganisationLink
from sqlalchemy.exc import IntegrityError
from uuid import UUID


async def add_or_update_user_role_organisation_link(
    link: UserOrganisationLink,
) -> UserOrganisationLink:
    with get_db_session() as session:
        try:
            # Tentative d'insertion du nouveau lien
            session.add(link)
            session.commit()
            session.refresh(link)
            return link
        except IntegrityError:
            # Si le lien existe déjà, on met à jour les informations
            session.rollback()

            # Recherche du lien existant
            existing_link = session.exec(
                select(UserOrganisationLink).where(
                    UserOrganisationLink.user_uuid == link.user_uuid,
                    UserOrganisationLink.orga_uuid == link.orga_uuid,
                )
            ).first()

            if existing_link:
                # Mise à jour des champs
                existing_link.role = link.role
                existing_link.updated_at = link.updated_at

                session.add(existing_link)
                session.commit()
                session.refresh(existing_link)
                return existing_link
            else:
                # Ce cas ne devrait pas arriver, mais on le gère par précaution
                raise ValueError(
                    "Le lien n'a pas pu être trouvé après la détection d'un conflit."
                )


async def get_user_role_for_organisation(
    user_uuid: UUID, orga_uuid: UUID
) -> UserOrganisationLink | None:
    with get_db_session() as session:
        statement = select(UserOrganisationLink).where(
            UserOrganisationLink.user_uuid == user_uuid,
            UserOrganisationLink.orga_uuid == orga_uuid,
        )
        result = session.exec(statement).first()
        return result
