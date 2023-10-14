from django.urls import path

import quiz.views as quiz_v
from . import views

# extra service for spielleiter
app_name = 'service'

urlpatterns = [
    # quizboard of some person
    path('quizTimetable/<int:spieler_id>/', quiz_v.index, name='quizTimetable'),

    # quiz BB
    path('quiz_BB/', views.quiz_BB, name='quiz_BB'),

    # dice
    path('random/', views.random, name='random'),
]
