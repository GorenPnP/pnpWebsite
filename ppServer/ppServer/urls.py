"""ppServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    path("500", views.error_500, name="test500"),
    path("404", views.error_404, name="test404"),
    path("418", views.error_418, name="test418"),

    path('auth/', include('auth_custom.urls')),
    path('accounts/', include('auth_custom.urls')),

    path('admin/', admin.site.urls),
    path('shop/', include('shop.urls')),
    path('wiki/', include('wiki.urls')),
    path('polls/', include('polls.urls')),
    path('character/', include('character.urls')),
    path('create/', include('create.urls')),
    path('log/', include('log.urls')),
    path('quiz/', include('quiz.urls')),
    path('service/', include('service.urls')),
    path('file/', include('fileserver.urls')),
    path('crafting/', include('crafting.urls')),
    path('time_space/', include('time_space.urls')),

    path('', include("base.urls")),
]

handler404 = views.error_404
handler500 = views.error_500
handler418 = views.error_418

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
