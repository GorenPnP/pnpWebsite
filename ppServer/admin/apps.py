from django.contrib.admin import apps


class AdminConfig(apps.AdminConfig):
    default_site = "admin.admin.AdminCustomSite"
