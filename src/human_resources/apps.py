from django.apps import AppConfig
from django.db.models.signals import post_save, pre_delete


class HumanResourcesConfig(AppConfig):
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'human_resources'

    def ready(self) -> None:
        from . import signals
        from distributor.models import Distributor
        from .models import Employee, Task

        # After creating new employee/distributor or update
        post_save.connect(signals.onAddingUpdatingEmployee, sender=Employee)
        post_save.connect(signals.onAddingUpdatingDistributor,
                          sender=Distributor)

        # Before deleting employee/distributor or task
        pre_delete.connect(signals.deleteUserAccount, sender=Employee)
        pre_delete.connect(signals.deleteUserAccount, sender=Distributor)
        pre_delete.connect(signals.deleteTaskRate, sender=Task)

        return super().ready()
