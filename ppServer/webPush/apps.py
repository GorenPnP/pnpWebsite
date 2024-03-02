from django.apps import AppConfig


class WebpushConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webPush'

    def ready(self):
        import webPush.signals