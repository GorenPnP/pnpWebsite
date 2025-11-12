from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm
)
from django.contrib.auth.models import User
from django.core.validators import EmailValidator

from base.crispy_form_decorator import crispy

from django_password_eye.widgets import PasswordEyeWidget

@crispy(form_tag=False)
class LoginForm(AuthenticationForm):
    def __init__(self, request = ..., *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        self.fields["password"].widget = PasswordEyeWidget()


@crispy(form_tag=False)
class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    email = forms.EmailField(max_length=200, validators=[EmailValidator], required=True)


@crispy(form_tag=False)
class ChangeEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)

    email = forms.EmailField(max_length=200, validators=[EmailValidator], required=True)


@crispy(form_tag=False)
class CrispyPasswordResetForm(PasswordResetForm):
    pass


@crispy(form_tag=False)
class ResetPasswordForm(SetPasswordForm):
    pass


@crispy(form_tag=False)
class ChangePasswordForm(PasswordChangeForm):
    pass
