import re
from django import template

numeric_test = re.compile(r"^\d+$")
register = template.Library()

@register.filter
def getattribute(value, arg):
    """Gets an attribute of an object dynamically from a string name"""

    if type(value) is dict and str(arg) in value:
        return value[str(arg)]
    if hasattr(value, str(arg)):
        return getattr(value, arg)
    elif hasattr(value, 'has_key') and value.has_key(arg):
        return value[arg]
    elif numeric_test.match(str(arg)) and len(value) > int(arg):
        return value[int(arg)]
    else:
        return None
