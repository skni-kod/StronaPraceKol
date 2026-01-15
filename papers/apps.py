from django.apps import AppConfig


class PapersConfig(AppConfig):
    name = 'papers'

    def ready(self):
        from .tasks import setup_scheduled_tasks
        setup_scheduled_tasks()
