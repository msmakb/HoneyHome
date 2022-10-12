from .models import Stock
from .views import MAIN_STORAGE_ID

def onMigratingStockModel(**kwargs):
    """
    Creating the main storage stock.
    """
    if not Stock.objects.all().exists():
        Stock.objects.create(id=MAIN_STORAGE_ID)
        print('  Main storage stock created')
