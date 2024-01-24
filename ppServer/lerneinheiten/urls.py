from django.urls import path

from . import views
from . import views_sp

app_name = 'lerneinheiten'

urlpatterns = [
    # path('', views.AccountListView.as_view(), name='index'),
    path('editor', views_sp.EditorIndexView.as_view(), name='editor_index'),
    path('editor/<int:pk>', views_sp.EditorPageView.as_view(), name='editor_page'),
]
