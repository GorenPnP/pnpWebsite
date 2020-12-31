from django.forms import ModelForm
from django.forms.widgets import CheckboxSelectMultiple, TextInput

from .models import Module

class ModuleForm(ModelForm):
	class Meta:
		model = Module
		fields = ('num', 'title', 'reward', 'description', 'prerequisite_modules') #, 'questions') TODO
		widgets = {
			'reward': TextInput(),
			'prerequisite_modules': CheckboxSelectMultiple()
		}

	def __init__(self, *args, **kwargs):

		super(ModuleForm, self).__init__(*args, **kwargs)

		if "instance" in self.__dict__:
			self.fields["prerequisite_modules"].queryset = Module.objects.exclude(id=self.instance.id)
			# self.fields["questions"].widget = MultiWidget(widgets=[TextInput for _ in range(self.instance.questions.all().count())])
