from django.contrib import admin
from django.utils.timezone import now

from shop.admin import ViewOnlyInLine
from .models import Question, Choice, QuestionSpieler


class OldChoiceInline(ViewOnlyInLine):

    model = Choice
    extra = 0
    readonly_fields = ["votes"]
    verbose_name = "Bestehende Möglichkeit"
    verbose_name_plural = "Bestehende Möglichkeiten"

    def has_add_permission(self, request):
        return False


class NewChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1
    readonly_fields = ["votes"]
    verbose_name = "neue Möglichkeit"
    verbose_name_plural = "neue Möglichkeiten"

    # empty queryset not to show old choice-entries
    def get_queryset(self, request):
        return Choice.objects.filter(id=-1)

    def has_add_permission(self, request):
        return True


class SpielerInline(admin.TabularInline):
    model = QuestionSpieler
    extra = 1
    readonly_fields = ["spieler"]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class QuestionAdmin(admin.ModelAdmin):
    fields = ['text', "anz_stimmen", 'pub_date', "deadline"]#, 'classes': ['collapse']}),
    inlines = [OldChoiceInline, NewChoiceInline, SpielerInline]
    list_display = ('text', 'pub_date', 'deadline', "umfrage_läuft")
    list_filter = ['pub_date']

    def get_readonly_fields(self, request, obj=None):
        if not request.user.groups.filter(name__iexact="spielleiter").exists():
            return ["text", "pub_date", "deadline", "anz_stimmen"]
        return super().get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        if not request.user.groups.filter(name__iexact="spielleiter").exists():
            return False
        return super().has_delete_permission(request, obj)

    def has_add_permission(self, request):
        if not request.user.groups.filter(name__iexact="spielleiter").exists():
            return False
        return super().has_change_permission(request)

    def get_queryset(self, request):
        if not request.user.groups.filter(name__iexact="spielleiter").exists():
            return Question.objects.filter(pub_date__gte=now())
        return super().get_queryset(request)


admin.site.register(Question, QuestionAdmin)
