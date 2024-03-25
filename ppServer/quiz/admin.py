from typing import Any, Optional
from django.contrib import admin
from django.db.models import OuterRef
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.html import format_html

from ppServer.utils import ConcatSubquery, get_filter

from .models import *


def save_selected(modeladmin, request, queryset):
    for q in queryset:
        q.save()
save_selected.short_description = "Ausgewählte Module speichern"
save_selected.allowed_permissions = ('change',)


class ModelStateFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = "Model State"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'state'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return tuple([(None, "All")] + module_state + [(106, "not passed")])

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == None:
            return queryset.all()
        if self.value() == 106:
            return queryset.exclude(state=6)
        
        return queryset.filter(state=self.value())



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

class ModuleInLine(admin.TabularInline):
    model = ModuleQuestion
    verbose_name = "Module"
    verbose_name_plural = "Modules"
    fields = ["module"]

    extra = 1


class SessionQuestionsInLine(admin.TabularInline):
    model = SpielerSession.questions.through
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request: HttpRequest, obj: Optional[Any] = ...) -> bool:
        return False
    def has_delete_permission(self, request: HttpRequest, obj: Optional[Any] = ...) -> bool:
        return False


class SubjectAdmin(admin.ModelAdmin):
    list_display = ["titel"]
    search_fields = ["titel"]


class TopicAdmin(admin.ModelAdmin):
    list_display = ["subject_", "titel"]
    list_filter = ["subject"]

    def subject_(self, obj):
        return obj.subject.titel
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("subject")


class QuestionAdmin(admin.ModelAdmin):
    list_display = ["text", "module_", "topic", "grade", "points", "answer_note", "images_included"]
    list_filter = [
        get_filter(Subject, "titel", ["topic__subject__titel"]),
        get_filter(Topic, "titel", ["topic__titel"]),
        "grade"
    ]
    search_fields = ["text", "topic__titel", "topic__subject__titel"]

    fieldsets = [
        ("Context", {'fields': ['topic', "grade", "points"]}),
        ("Question", {"fields": ["text", "answer_note", "images", "files"]}),
        ("Permissions", {"fields": ["allow_text", "allow_upload"]})
    ]

    inlines = [MultipleChoiceFieldInLine, ModuleInLine]

    def images_included(self, obj):
        if obj.images.exists(): return True

        for a in obj.multiplechoicefield_set.all():
            if a.img: return True

        return False

    # to show properties as pretty boolean-vals
    images_included.boolean = True


    def module_(self, obj):
        return obj.modulenames or self.get_empty_value_display()
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("topic__subject", "images", "multiplechoicefield_set").annotate(
            modulenames = ConcatSubquery(ModuleQuestion.objects.prefetch_related("module").filter(question=OuterRef("id")).values("module__title"), ", ")
        )

class ModuleAdmin(admin.ModelAdmin):
    list_display = ["icon_", "title", "num", "max_points", "reward", "prerequisites_"]
    list_display_links = ("icon_", "title")
    search_fields = ["title", "num", "prerequisite_modules__title"]

    exclude = ["max_points"]
    inlines = [QuestionsInLine]

    def prerequisites_(self, obj):
        return obj.prerequesitenames or self.get_empty_value_display()

    def icon_(self, obj):
        return format_html('<img src="{0}" style="max-width: 32px; max-height:32px;" />'.format(obj.icon.img.url)) if obj.icon else "-"
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("icon").annotate(
            prerequesitenames = ConcatSubquery(Module.objects.filter(module=OuterRef("id")).values("title"), ", "),
        )
    icon_.allow_tags = True

    actions = [save_selected]


class SpielerModuleAdmin(admin.ModelAdmin):
    list_display = ["spieler", "module", "state", "optional", "spent_reward", "spent_reward_larp", "_reward", "achieved_points"]
    list_filter = ["spieler", "module", ModelStateFilter]
    search_fields = ["spieler__name", "module__title", "state"]
    list_editable = ["spent_reward", "spent_reward_larp"]

    exclude = ["sessions"]

    def _reward(self, obj):
        return obj.module.reward
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("spieler", "module")


class SpielerSessionAdmin(admin.ModelAdmin):
    list_display = ["spielerModule", "current_question", "started"]
    list_filter = ["spielerModule__spieler", "spielerModule__module"]
    search_fields = ["spielerModule__spieler__name", "spielerModule__module__title"]

    exclude = ["questions"]
    readonly_fields = ["spielerModule"]
    inlines = [SessionQuestionsInLine]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("spielerModule__spieler", "spielerModule__module")


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

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("spieler", "current_session__spielerModule__spieler", "current_session__spielerModule__module")


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
