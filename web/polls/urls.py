from django.urls import path
from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.options, name='index'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
]

