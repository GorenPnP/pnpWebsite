from django.contrib import messages
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator

from character.models import *

from ..decorators import is_erstellung_done
from ..forms import PersonalForm
from ..mixins import LevelUpMixin


@method_decorator([is_erstellung_done], name="dispatch")
class GenericPersonalView(LevelUpMixin, TemplateView):
    template_name = "levelUp/personal.html"

    def get_context_data(self, *args, **kwargs):
        char = self.get_character()
        return super().get_context_data(*args, **kwargs, form = PersonalForm(instance=char), topic = "Persönliches")


    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        char = self.get_character()

        form = PersonalForm(request.POST, request.FILES, instance=char)
        form.full_clean()
        if form.is_valid():
            form.save()
            messages.success(request, "Erfolgreich gespeichert")

        return redirect(request.build_absolute_uri())