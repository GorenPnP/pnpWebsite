from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import EmailValidator


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    email = forms.EmailField(max_length=200, validators=[EmailValidator], required=True)


class ChangeEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)

    email = forms.EmailField(max_length=200, validators=[EmailValidator], required=True)