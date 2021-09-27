from django.conf.urls import url
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetCompleteView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetView

from . import views

app_name = 'auth'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='auth/login.html'), name="login"),
    path('logout/', LogoutView.as_view(next_page='base:index'), name='logout'),

    # signup with email confirmation
    path('signup/', views.signup, name='signup'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),

    # forgot password
    path('password_reset/', PasswordResetView.as_view(template_name='auth/password_reset.html', email_template_name = 'auth/password_reset_email.html', success_url='/auth/password_reset/done'), name="reset_password"),
    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), name="password_reset_done"),
    path('password_reset/<uidb64>/<token>', PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html', success_url="/auth/password_reset/complete"), name="password_reset_confirm"),
    path('password_reset/complete/', PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), name="password_reset_complete"),
]
