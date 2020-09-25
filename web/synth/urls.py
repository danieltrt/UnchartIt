from django.urls import path
from . import views

app_name = 'synth'
urlpatterns = [
    path('', views.index, name='index'),
]

