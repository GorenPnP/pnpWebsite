from django.apps import apps
from django.db.models import Model


def get_ModelNameConverter(app: str, model_list: list[Model] = []):
    class ModelNameConverter:
        def __init__(self):
            self.app = app
            self.app_models = {m._meta.model_name: m for m in apps.get_app_config(self.app).get_models() if not model_list or m in model_list}
            self.regex = "|".join(self.app_models.keys())

        def to_python(self, value: str) -> Model:
            if value not in self.app_models: raise ValueError()
            return self.app_models[value]

        def to_url(self, value: Model) -> str:
            if value not in self.app_models.values(): raise ValueError()
            return value._meta.model_name
    return ModelNameConverter