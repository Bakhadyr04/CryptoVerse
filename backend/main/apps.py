from django.apps import AppConfig
from cryptoverse.tasks import setup_periodic_tasks

class MainConfig(AppConfig):
    name = 'main'

    def ready(self):
        setup_periodic_tasks()
