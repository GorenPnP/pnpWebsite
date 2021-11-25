from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


# Define a new User admin
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("is_superuser", "groups_",)

    def groups_(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])
    admin.boolean = True

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
