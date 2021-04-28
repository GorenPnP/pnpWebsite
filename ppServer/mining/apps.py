from django.apps import AppConfig


class MiningConfig(AppConfig):
    name = 'mining'

    def ready(self):
        import mining.signals