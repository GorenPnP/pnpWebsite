from django.urls import path

from . import views
from . import views_sp

app_name = 'lerneinheiten'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>', views.PageView.as_view(), name='page'),
    
    path('editor', views_sp.EditorIndexView.as_view(), name='editor_index'),
    path('editor/<int:pk>', views_sp.EditorPageView.as_view(), name='editor_page'),
    path('access/', views_sp.AccessPageView.as_view(), name='access'),
    
    path('editor/new_einheit', views_sp.new_einheit, name='new_einheit'),
    path('editor/edit_einheit/<int:pk>', views_sp.edit_einheit, name='edit_einheit'),
    path('editor/new_page', views_sp.new_page, name='new_page'),
    path('editor/image_upload/<int:page_id>', views_sp.image_upload, name='image_upload'),

    path('inquiry_form/<int:page_id>', views.inquiry_form, name='inquiry_form'),
]
