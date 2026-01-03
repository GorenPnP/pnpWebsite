from django.contrib import admin

from .models import Question, Choice, QuestionSpieler


class OldChoiceInline(admin.TabularInline):

    model = Choice
    extra = 0
    readonly_fields = ["votes"]
    verbose_name = "Bestehende Möglichkeit"
    verbose_name_plural = "Bestehende Möglichkeiten"

    def has_add_permission(self, request, obj=None):
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

    def has_add_permission(self, request, obj=None):
        return True


class SpielerInline(admin.TabularInline):
    model = QuestionSpieler
    extra = 1
    readonly_fields = ["spieler"]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class QuestionAdmin(admin.ModelAdmin):
    fields = ['text', "anz_stimmen", 'pub_date', "deadline", "allow_multiple_selection", "show_result_to_user"]
    inlines = [OldChoiceInline, NewChoiceInline, SpielerInline]
    list_display = ('text', 'pub_date', 'deadline', "umfrage_läuft")
    list_filter = ['pub_date']


admin.site.register(Question, QuestionAdmin)
