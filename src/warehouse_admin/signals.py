from .models import Stock
from main import constants


def onMigratingStockModel(**kwargs):
    """
    Creating the main storage stock.
    """
    if not Stock.objects.all().exists():
        Stock.objects.create(id=constants.MAIN_STORAGE_ID)
        print('  Main storage stock created')
