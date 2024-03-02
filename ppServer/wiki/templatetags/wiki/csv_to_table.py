from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def csv_to_table(csv: str, delimiter: str = ";", table_classes="table table-dark table-striped table-hover"):
    html = f"<table class='{table_classes}'><thead>"

    for i, row in enumerate(csv.split("\n")):
        if i == 1: html += "</thead><tbody>"
        
        html += "<tr>"
        html += "<th>" if i == 0 else "<td>"

        html += ("</th><th>" if i == 0 else "</td><td>").join(row.split(delimiter)) + ("</th>" if i == 0 else "</td>")

    return format_html(html + "</tbody></table>")