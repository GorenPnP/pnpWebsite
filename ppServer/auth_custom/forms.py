from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm
)
from django.contrib.auth import get_user_model
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
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')

    email = forms.EmailField(max_length=200, validators=[EmailValidator], required=True)

    def clean_email(self):
        if self.cleaned_data["email"] and self.model.objects.filter(email=self.cleaned_data["email"]).exists():
            raise forms.ValidationError("Die E-Mail ist bereits vergeben")
        return self.cleaned_data["email"]


@crispy(form_tag=False)
class ChangeEmailForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
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
