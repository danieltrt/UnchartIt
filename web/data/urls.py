from django.urls import path
from . import views

app_name = 'data'
urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('display/<int:id>/', views.display, name='display')
]

