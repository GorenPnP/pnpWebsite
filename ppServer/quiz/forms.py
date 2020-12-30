from django.forms import ModelForm
from django.forms.widgets import TextInput

from .models import Module

class ModuleForm(ModelForm):
		class Meta:
			model = Module
			fields = ('num', 'title', 'reward', 'description')
			widgets = {'reward': TextInput()}
