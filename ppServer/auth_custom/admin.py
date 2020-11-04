from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group


# Define a new User admin
class UserAdmin(UserAdmin):
    def has_add_permission(self, request):
        if request.user.groups.filter(name__iexact="shop angucken").exists():
            return False
        else:
            return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if request.user.groups.filter(name__iexact="shop angucken").exists():
            return False
        else:
            return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name__iexact="shop angucken").exists():
            return False
        else:
            return super().has_change_permission(request, obj)


class GroupAdmin(GroupAdmin):

    def has_add_permission(self, request):
        if request.user.groups.filter(name__iexact="shop angucken").exists():
            return False
        else:
            return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if request.user.groups.filter(name__iexact="shop angucken").exists():
            return False
        else:
            return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name__iexact="shop angucken").exists():
            return False
        else:
            return super().has_change_permission(request, obj)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
