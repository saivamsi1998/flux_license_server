from django.apps import AppConfig
from . import scheduler

class FluxConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'flux'
    def ready(self):
        scheduler.start_scheduler()
