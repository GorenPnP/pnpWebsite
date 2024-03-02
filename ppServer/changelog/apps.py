from django.apps import AppConfig


class ChangelogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'changelog'

    def ready(self):
        import changelog.signals