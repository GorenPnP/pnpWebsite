from django.apps import AppConfig


class CreateConfig(AppConfig):
    name = 'create'

    def ready(self):
        import create.signals
