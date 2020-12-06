from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetDoneView, PasswordResetView

from . import views

app_name = 'auth'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='auth/login.html')),
    path('logout/', LogoutView.as_view(next_page='base:index'), name='logout'),
    path('signup/', views.signup, name='signup'),

    # Need to supply a email for each user beforehand. Has to be the one entered in there
    # path('password_reset/', PasswordResetView.as_view(success_url="/auth/password_reset_done"), name='password_reset'),
    # path('password_reset_done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
]
