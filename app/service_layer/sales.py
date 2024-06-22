from models.sales import SaleCreate, SaleRead, SaleUpdate


async def create_sale(sale_to_create : SaleCreate) -> SaleRead | None:
    """
    Focntion de création de vente aux enchères.
    Elle est obligatoirement associée à une organisation.
    """

async def update_sale(sale_to_update : SaleUpdate) -> SaleRead | None:
    """
    Fonction de modification des ventes
    """

    