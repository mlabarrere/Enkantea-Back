from app.models.organisations import OrganisationRead, OrganisationUpdate


async def add_user_to_organisation() -> OrganisationRead | None:
    """
    Ajouter dans la table
    """
