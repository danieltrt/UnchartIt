from django.shortcuts import render
from .src.predict import *
# Create your views here.

def index(request):
    return render(request, 'data.html')

def upload(request):
    for file_name in list(request.FILES.keys()):
        f = request.FILES[file_name]
        res = chart_to_table(f, 0, 1)

    return render(request, 'data.html')