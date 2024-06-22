from app.models.users import UserRead, UserCreate, UserUpdate
from app.models.organisations import OrganisationCreate
from data_layer.users import create_user
from data_layer.organisations import create_organisation

async def get_user(user_to_get : UserRead) -> UserRead | None:
    """
    Simple get User
    """
    return None

async def new_user(user_to_create : dict) -> UserRead | None:
    """
    Un nouvel usager est toujours composé d'un usager à créer, et de son son espace personnel (organisation).
    Cette dernière permet d'ajouter des lots, des ventes ext.
    """
    # Step 1 : On créé l'usager
    user_to_create = UserCreate(**user_to_create)
    user_to_create = create_user(user_create=user_to_create)
    # Step 2 : Créer son Organisation par défault
    orga_name = f"Organisation de {user_to_create['last_name']}"
    orga_object = OrganisationCreate(**{'company_name':orga_name})
    user_orga = create_organisation(organisation_create=orga_object)
    # Step 3 : Update Table de link entre User et Orga
    # Step 4 : Return Statuts
    return None

async def update_user(user_to_update : UserUpdate) -> UserRead | None:
    """
    Fonction qui ne met à jour uniquement les informations visibles de l'usager.
    Aucune action sur les organisations
    """
    return None

async def delete_user(user_to_delete : UserUpdate) -> UserRead | None:
    """
    Fonction qui supprime un usager avec les critères suivants :
    Pour chaque organisation dans laquelle il est, il faut vérifier si :
    - il n'est pas le dernier user dans l'organisation, auquel
    """
    return None


