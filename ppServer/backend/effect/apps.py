from django.apps import AppConfig


class EffectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'effect'

    def ready(self):
        import effect.signals