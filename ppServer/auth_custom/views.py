from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
import six
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from ppServer.decorators import verified_account

from .forms import ChangeEmailForm, SignupForm

User = get_user_model()

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )
account_activation_token = TokenGenerator()




def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        form.full_clean()
        if form.is_valid():
            user = form.save(commit=False)

            if User.objects.filter(email = user.email).exists():
                return redirect('auth:signup_done')

            # give user spieler permissions
            user.is_active = False
            user.is_staff = True
            user.save()

            my_group = Group.objects.get(name='Spieler') 
            my_group.user_set.add(user)

            # send email
            current_site = get_current_site(request)
            mail_subject = 'Account bestätigen'
            message = render_to_string('auth/email/email_confirmation.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return redirect('auth:signup_done')
    else:
        form = SignupForm()
    return render(request, 'auth/signup.html', {'form': form})



@verified_account
def change_email(request):
    old_email = request.user.email
    
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST)
        form.full_clean()
        if form.is_valid():
            new_email = form.cleaned_data['email']
            if new_email == old_email:
                messages.error(request, "Deine Eingabe ist bereits deine E-Mail. Wenn du sie ändern willst, musst du was Anderes eingeben.")
                return redirect('auth:change_email')

            user = request.user
            user.email = new_email
            user.save(update_fields=["email"])

            current_site = get_current_site(request)
            mail_subject = 'Neue Email bestätigen'
            message = render_to_string('auth/email/email_confirmation.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return redirect('auth:change_email_done')
    else:
        form = ChangeEmailForm(initial={"email": old_email})
    return render(request, 'auth/change_email.html', {'form': form})



def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        
        # activate user
        user.is_active = True
        user.save(update_fields=["is_active"])

        # auto-login
        login(request, user)
        return redirect('base:index')
    else:
        return HttpResponse('Aktivierungslink ist nicht korrekt!')
    

class ChangePasswordView(PasswordChangeView):
    def form_valid(self, form):
        messages.success(self.request, "Passwort erfolgreich geändert")
        return super().form_valid(form)