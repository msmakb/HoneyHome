from .models import Stock
from main import constant


def onMigratingStockModel(**kwargs):
    """
    Creating the main storage stock.
    """
    if not Stock.objects.all().exists():
        Stock.objects.create(id=constant.MAIN_STORAGE_ID)
        print('  Main storage stock created')
