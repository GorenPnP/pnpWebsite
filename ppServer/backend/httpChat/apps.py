from django.apps import AppConfig


class HttpchatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'httpChat'

    def ready(self):
        import httpChat.signals