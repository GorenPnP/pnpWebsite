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
    path("404", views.error_404, name="test404"),

    path('admin/', admin.site.urls),
    path('auth/', include('auth_custom.urls')),
    path('accounts/', include('auth_custom.urls')),

    path('cards/', include('cards.urls')),
    path('changelog/', include('changelog.urls')),
    path('character/campaign/', include('campaign.urls')),
    path('character/export/', include('characterExport.urls')),
    path('character/', include('character.urls')),
    path('chat/', include('chat.urls')),
    path('crafting/', include('crafting.urls')),
    path('create/', include('create.urls')),
    path('file/', include('fileserver.urls')),
    path('chat2.0/', include('httpChat.urls')),
    path('log/', include('log.urls')),
    path('mining/', include('mining.urls')),
    path('news/', include('news.urls')),
    path('planner/', include('planner.urls')),
    path('polls/', include('polls.urls')),
    path('quiz/', include('quiz.urls')),
    path('service/', include('service.urls')),
    path('shop/', include('shop.urls')),
    path('time_space/', include('time_space.urls')),
    path('wiki/', include('wiki.urls')),

    path('__debug__/', include('debug_toolbar.urls')),

    path('', include("base.urls")),
]

handler404 = views.error_404

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
