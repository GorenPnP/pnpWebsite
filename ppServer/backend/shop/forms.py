from crispy_forms.layout import Layout, Div, Field, Submit, Reset, Fieldset
from django_filters import FilterSet

from base.crispy_form_decorator import crispy

from .models import *

class ShopFilter(FilterSet):
    """ adds crispy to django-filter model filter for shop items """
    def get_form_class(self):

        @crispy(form_method="get")
        class Form(super().get_form_class()):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.helper.layout = Layout(
                    *self.fields.keys(),
                    Submit('submit', "Filtern", css_class="btn btn-light me-1"),
                    Reset('reset', "Zurücksetzen", css_class="btn btn-outline-light"),
                )
        return Form
