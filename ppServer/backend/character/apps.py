from django.apps import AppConfig


class CharacterConfig(AppConfig):
    name = 'character'

    def ready(self):
        import character.signals
