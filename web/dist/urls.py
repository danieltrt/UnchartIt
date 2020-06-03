from django.urls import path
from . import views

app_name = 'dist'
urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),

    path('options/<int:choice_id>/', views.options, name='options_opt'),
    path('yesno/<int:choice_id>/', views.yesno, name='yesno_opt'),

    path('options/<int:choice_id>/<int:iter_n>', views.options, name='options_iter'),
    path('yesno/<int:choice_id>/<int:iter_n>/', views.yesno, name='yesno_iter'),

    path('submit/<int:question_id>/', views.submit, name='submit'),
]

