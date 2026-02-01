import random, re, string

from django import template
from django.contrib.staticfiles import finders
from django.template.loader import render_to_string

register = template.Library()

@register.tag
def resources(parser, token):
    """
    call in html templates (icon="..." is optional, but has to start with "static/")
    {% resources icon="static/res/img/icon questionmark.svg" %}
        ...
    {% endresources %}
    """

    endings = [r"\.svg", r"\.png"]
    match = re.search(fr" icon=[\"']static/(?P<icon>([a-zA-Z0-9_\- ]+/)+[a-zA-Z0-9_\- ]*(({')|('.join(endings)})))[\"']", token.contents)
    icon = match.group("icon") if match else "res/img/icon questionmark.svg"

    nodelist = parser.parse(('endresources',))
    parser.delete_first_token()
    return ResourcesNode(nodelist, icon)

class ResourcesNode(template.Node):
    def __init__(self, nodelist, icon):

        self.offcanvas_id = f"characterResources-{''.join(random.choices(string.ascii_letters + string.digits, k=10))}"
        self.nodelist = nodelist

        with open(finders.find(icon), 'r') as f:
            self.icon = f.read()
 
    def render(self, context):
        return render_to_string("levelUp/_resources.html", context={
            "res": self.nodelist.render(context),
            "offcanvas_id": self.offcanvas_id,
            "icon": self.icon,
        })
