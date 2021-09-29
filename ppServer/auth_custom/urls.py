from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetCompleteView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetView
from django.views.generic.base import TemplateView

from . import views

app_name = 'auth'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='auth/login.html'), name="login"),
    path('logout/', LogoutView.as_view(next_page='base:index'), name='logout'),

    # signup with email confirmation
    path('signup/', views.signup, name='signup'),
    path('signup/done/', TemplateView.as_view(template_name="auth/signup_done.html"), name='signup_done'),
    # change email with confirmation
    path('change_email/', views.change_email, name='change_email'),
    path('change_email/done/', TemplateView.as_view(template_name="auth/change_email_done.html"), name='change_email_done'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),

    # forgot password
    path('password_reset/', PasswordResetView.as_view(template_name='auth/password_reset.html', email_template_name = 'auth/email/password_reset_email.html', success_url='/auth/password_reset/done'), name="reset_password"),
    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), name="password_reset_done"),
    path('password_reset/<uidb64>/<token>', PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html', success_url="/auth/password_reset/complete"), name="password_reset_confirm"),
    path('password_reset/complete/', PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), name="password_reset_complete"),
]
