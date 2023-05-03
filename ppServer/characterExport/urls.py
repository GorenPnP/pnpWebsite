from django.urls import path

from . import views

app_name = 'character_export'

urlpatterns = [
	path('<int:pk>', views.CharacterExportView.as_view(), name='export'),
]
