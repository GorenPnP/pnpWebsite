from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from . import views

app_name = 'auth'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='auth/login.html')),
    path('logout/', LogoutView.as_view(next_page='base:index'), name='logout'),
    path('signup/', views.signup, name='signup'),
]
