from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.tag
def resources(parser, token):
    nodelist = parser.parse(('endresources',))
    parser.delete_first_token()
    return ResourcesNode(nodelist)

class ResourcesNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
 
    def render(self, context):
        return render_to_string("levelUp/_resources.html", context={"res": self.nodelist.render(context)})
