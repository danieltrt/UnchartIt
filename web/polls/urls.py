from django.urls import path
from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.index, name='index'),
    path('options/', views.options, name='options'),
    path('yesno/', views.yesno, name='yesno'),
    path('options/<int:choice_id>/', views.options, name='options_opt'),
    path('yesno/<int:choice_id>/', views.yesno, name='yesno_opt'),
    path('submit/<int:question_id>/', views.submit, name='submit'),
]

