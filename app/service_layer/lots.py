from models.lots import LotRead, LotCreate, LotUpdate
from models.organisations import OrganisationCreate, OrganisationRead, OrganisationUpdate
from data_layer.lots import create_lot, read_lot ,update_lot, delete_lot 

"""
Création et gestion des Lots
- Création d'un Lot associé à une Organisation spécifique
- Association d'un Lot à un Client de la même Organisation
- Vérification que les Lots ne sont visibles que par les utilisateurs de l'Organisation propriétaire
"""

async def add_lot_to_organisation(lot_to_add : LotCreate, mother_organisation : OrganisationRead) -> None :
    """
    Création d'un Lot associé à une Organisation spécifique.
    TODO : arbitrer si on fait l'authentification ici ou dans la partie weblayer
    """
    return None


"""
Relation Lots-Clients
- Affichage des Lots associés à un Client spécifique (dans le contexte d'une Organisation)
- Possibilité d'associer ou de dissocier un Client à un Lot
"""
async def link_lots_to_seller(lot_to_link : list(LotUpdate), seller : SellerRead) -> LotRead | None:
    """
    Associe une liste de lots à un vendeur
    """
    return None

async def unlink_lots_from_seller(lot_to_link : list(LotUpdate), seller : SellerRead) -> LotRead | None:
    """
    Associe une liste de lots à un vendeur
    """
    return None


"""
Relation Lots-Organisations
- Filtrage des Lots par Organisation pour les utilisateurs ayant accès à plusieurs Organisations
- Impossibilité de voir ou d'accéder aux Lots d'autres Organisations
"""

"""
Relation Lots-Factures (Invoices)
- Création de Factures basées sur un ou plusieurs Lots d'une vente
- Affichage de l'historique des Factures liées à un Lot spécifique
"""

"""
Relation Lots-Ventes (Sales)
- Enregistrement des ventes liées à un Lot spécifique
- Calcul et affichage des statistiques de vente par Lot
"""

"""
Gestion des accès multi-organisations
- Possibilité pour un utilisateur de basculer entre différentes Organisations
- Adaptation de la vue des Lots en fonction de l'Organisation active
"""

"""
Confidentialité inter-organisations
- Garantie que les informations des Lots (y compris les Clients associés) ne sont pas visibles par les autres Organisations
"""

"""
Recherche et filtrage des Lots
- Recherche de Lots par critères spécifiques (nom, date, client associé, etc.) dans le contexte d'une Organisation
"""

"""
Reporting et analyse
- Génération de rapports sur les Lots par Organisation
- Analyse comparative des performances des Lots au sein d'une Organisation
"""

"""
Gestion des versions et historique des Lots
- Suivi des modifications apportées aux Lots
- Historique des changements d'association Client-Lot
"""

"""
Workflow des Lots
- Gestion du cycle de vie des Lots (ex: création, en cours, terminé, archivé)
- Notifications liées aux changements d'état des Lots
"""

"""
Intégration avec le système de permissions
- Définition et application de rôles spécifiques pour la gestion des Lots au sein de chaque Organisation
"""

"""
Duplication et transfert de Lots
- Possibilité de dupliquer un Lot au sein de la même Organisation
- Impossibilité de transférer un Lot d'une Organisation à une autre
"""

"""
Gestion des conflits
- Mécanismes pour gérer les tentatives d'accès ou de modification simultanées d'un Lot
"""

"""
Archivage des Lots
- Processus d'archivage des Lots anciens ou inactifs, tout en maintenant la confidentialité inter-organisations
"""