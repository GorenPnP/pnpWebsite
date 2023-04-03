
from typing import Any

from django import template, forms


register = template.Library()


@register.filter
def getField(form: forms.Form, fieldname: str) -> Any:
    for key in form.fields.keys():

        if key.split("__")[0] == fieldname:
            return form.fields[key].get_bound_field(form, key)