from django.apps import AppConfig


class LerneinheitenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lerneinheiten'

    def ready(self):
        import lerneinheiten.signals