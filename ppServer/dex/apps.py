from django.apps import AppConfig


class DexConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dex'

    def ready(self):
        import dex.monster.admin
        import dex.monster.signals