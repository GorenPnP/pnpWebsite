from django.urls import path

from .views import *
from .views_sp import *

app_name = 'quiz'

urlpatterns = [
	path('sp', sp_index, name='sp_index'),
	path('sp/questions', sp_questions, name="sp_questions"),
	path('sp/modules', sp_modules, name="sp_modules"),
	path('sp/correct/<int:id>', sp_correct, name="sp_correct"),


	path('', index, name='index'),
	path('question', question, name='question'),
	path('done', session_done, name='session_done'),
	path('review/<int:id>', review, name="review"),
	path('scoreBoard', score_board, name='scoreBoard'),
]
