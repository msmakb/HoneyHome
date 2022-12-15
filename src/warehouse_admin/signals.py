from .models import Stock
from main import constants
from main.utils import setCreatedByUpdatedBy


def onMigratingStockModel(**kwargs):
    """
    Creating the main storage stock.
    """
    if not Stock.objects.all().exists():
        main_stock = Stock.objects.create(id=constants.MAIN_STORAGE_ID)
        setCreatedByUpdatedBy("System on initializing", main_stock)
        print('  Main storage stock created')
