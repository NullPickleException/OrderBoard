from django.apps import AppConfig


class OrderboardConfig(AppConfig):
    name = "orderboard"

    def ready(self):
        from .backup import start_backup_worker

        start_backup_worker()