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
    fields = ["question", "num"]

    extra = 1


class SessionQuestionsInLine(admin.TabularInline):
    model = SpielerSession.questions.through
    extra = 0
    can_delete = False


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
    list_filter = ["topic__subject", "topic", "grade"]
    search_fields = ["text", "topic__titel", "topic__subject__titel"]

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
    search_fields = ["title", "num", "prerequisite_modules__title"]

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
    search_fields = ["spieler__name", "module__title", "state"]

    exclude = ["sessions"]


class SpielerSessionAdmin(admin.ModelAdmin):
    list_display = ["spielerModule", "current_question", "started"]
    list_filter = ["spielerModule__spieler", "spielerModule__module"]
    search_fields = ["spielerModule__spieler__name", "spielerModule__module__title"]

    exclude = ["questions"]
    readonly_fields = ["spielerModule"]
    inlines = [SessionQuestionsInLine]


class SpielerQuestionAdmin(admin.ModelAdmin):
    list_display = ["spieler", "question", "achieved_points"]
    list_filter = ["spieler", "question"]
    search_fields = ["question__text", "question__topic__titel", "question__topic__subject__titel", "spieler__name"]

    fieldsets = [
        ("Basis", {'fields': ["question", "spieler",  "achieved_points", "in_module"]}),
        ("Antwort", {'fields': ["answer_mc", "answer_text", "answer_img", "answer_file"]}),
        ("Korrektur", {'fields': ["correct_mc", "correct_text", "correct_img", "correct_file"]})
    ]
    readonly_fields = ["spieler", "question", "in_module"]

    def in_module(self, obj):
        return ", ".join(["{} (NR. {})".format(mq.module.title, mq.num) for mq in obj.moduleQuestions.all()])


class RelQuizAdmin(admin.ModelAdmin):
    list_display = ("spieler", "quiz_points_achieved", "current_session")


class DataAdmin(admin.ModelAdmin):
    search_fields = ["name"]
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
