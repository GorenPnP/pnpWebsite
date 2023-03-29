from django.urls import path

from . import views, views_sp

app_name = 'quiz'

urlpatterns = [
	path('sp', views_sp.sp_index, name='sp_index'),
	path('sp/questions', views_sp.sp_questions, name="sp_questions"),

	path('sp/modules', views_sp.SpModulesView.as_view(), name="sp_modules"),
	path('sp/correct/<int:id>', views_sp.sp_correct, name="sp_correct"),
	path('sp/correct/<int:id>/<int:question_index>', views_sp.sp_correct, name="sp_correct_index"),
	path('sp/old_answer/<int:sp_mo_id>/<int:question_id>/<int:question_index>', views_sp.old_answer, name="sp_old_answer"),


	path('', views.index, name='index'),
	path('question', views.question, name='question'),
	path('done', views.session_done, name='session_done'),
	path('review/<int:id>', views.review, name="review"),
	path('review_done', views.session_done, name='review_done'),
	path('scoreBoard', views.score_board, name='scoreBoard'),
]
