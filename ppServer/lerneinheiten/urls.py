from django.urls import path

from . import views
from . import views_sp

app_name = 'lerneinheiten'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>', views.PageView.as_view(), name='page'),
    
    path('editor', views_sp.EditorIndexView.as_view(), name='editor_index'),
    path('editor/<int:pk>', views_sp.EditorPageView.as_view(), name='editor_page'),
    
    path('editor/new_einheit', views_sp.new_einheit, name='new_einheit'),
    path('editor/edit_einheit/<int:pk>', views_sp.edit_einheit, name='edit_einheit'),
    path('editor/new_page', views_sp.new_page, name='new_page'),
]
