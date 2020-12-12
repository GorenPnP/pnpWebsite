from django.contrib import admin
from django.utils.html import format_html

from .models import *


def save_selected(modeladmin, request, queryset):
    for q in queryset:
        q.save()
save_selected.short_description = "Ausgewählte Module speichern"
save_selected.allowed_permissions = ('change',)


class MultipleChoiceFieldInLine(admin.TabularInline):
    model = MultipleChoiceField
    fields = ["img", "text"]
    extra = 5


class QuestionsInLine(admin.TabularInline):
    model = ModuleQuestion
    verbose_name = "Question"
    verbose_name_plural = "Questions"
    extra = 1


class SessionQuestionsInLine(admin.TabularInline):
    model = SpielerSession.questions.through
    extra = 0


class SubjectAdmin(admin.ModelAdmin):
    list_display = ["titel"]
    search_fields = ["titel"]


class TopicAdmin(admin.ModelAdmin):
    list_display = ["subject_", "titel"]
    list_filter = ["subject"]

    def subject_(self, obj):
        return obj.subject.titel


class QuestionAdmin(admin.ModelAdmin):
    list_display = ["text", "module_", "topic", "grade", "points", "answer_note", "images_included"]
    list_filter = ["topic", "grade"]
    list_display_links = ("topic", )

    list_editable = ["topic", "grade", "points"]
    list_display_links = ["text"]

    fieldsets = [
        ("Context", {'fields': ['topic', "grade", "points"]}),
        ("Question", {"fields": ["text", "answer_note", "images", "files"]}),
        ("Permissions", {"fields": ["allow_text", "allow_upload"]})
        ]

    inlines = [MultipleChoiceFieldInLine]

    def images_included(self, obj):
        if obj.images.exists(): return True

        for a in obj.multiplechoicefield_set.all():
            if a.img: return True

        return False

    # to show properties as pretty boolean-vals
    images_included.boolean = True


    def module_(self, obj):
        mqs = ModuleQuestion.objects.filter(question=obj)
        return ", ".join([mq.module.__str__() for mq in mqs]) if mqs.count() else "-"

class ModuleAdmin(admin.ModelAdmin):
    list_display = ["icon_", "title", "num", "max_points", "reward", "prerequisites_"]
    list_display_links = ("icon_", "title")

    exclude = ["max_points"]
    inlines = [QuestionsInLine]

    def prerequisites_(self, obj):
        return ", ".join([p.title for p in obj.prerequisite_modules.all()]) if obj.prerequisite_modules.exists() else "-"

    def icon_(self, obj):
        return format_html('<img src="{0}" style="max-width: 32px; max-height:32px;" />'.format(obj.icon.img.url)) if obj.icon else "-"
    icon_.allow_tags = True

    actions = [save_selected]


class SpielerModuleAdmin(admin.ModelAdmin):
    list_display = ["spieler", "module", "state", "optional", "achieved_points"]
    list_filter = ["spieler", "module", "state"]

    readonly_fields = ["sessions"]


class SpielerSessionAdmin(admin.ModelAdmin):
    list_display = ["spielerModule", "current_question", "started"]

    exclude = ["questions"]
    inlines = [SessionQuestionsInLine]


class SpielerQuestionAdmin(admin.ModelAdmin):
    pass

class RelQuizAdmin(admin.ModelAdmin):
    list_display = ("spieler", "quiz_points_achieved", "current_session")


class DataAdmin(admin.ModelAdmin):
    exclude = ["name"]

admin.site.register(RelQuiz, RelQuizAdmin)
admin.site.register(Image, DataAdmin)
admin.site.register(File, DataAdmin)

admin.site.register(Subject, SubjectAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(SpielerModule, SpielerModuleAdmin)
admin.site.register(SpielerSession, SpielerSessionAdmin)
admin.site.register(SpielerQuestion, SpielerQuestionAdmin)
