from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from django.db.models import OuterRef

from ppServer.utils import ConcatSubquery


# Define a new User admin
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("is_active", "is_superuser", "groupnames",)

    def get_queryset(self, request):
        qs = Group.objects.filter(user__id=OuterRef("id")).values("name")

        return super().get_queryset(request).annotate(
            groupnames = ConcatSubquery(qs, separator=", ")
        )
    
    @admin.display(ordering="groupnames")
    def groupnames(self, obj):
        return obj.groupnames
    admin.boolean = True

# Re-register UserAdmin
User = get_user_model()
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
