from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def update_querystring(context, **kwargs):
    """
    Creates a URL (containing only the querystring [including "?"]) derived
    from the current URL's querystring, by updating it with the provided
    keyword arguments.

    Example (imagine URL is ``/abc/?gender=male&name=Tim``)::

        {% querystring "name"="Diego" "age"=20 %}
        ?name=Diego&gender=male&age=20
    """
    request = context['request']
    updated = request.GET.copy()
    for k, v in kwargs.items():  # have to iterate over and not use .update as it's a QueryDict not a dict
        updated[k] = v

    return '?{}'.format(updated.urlencode()) if updated else ''