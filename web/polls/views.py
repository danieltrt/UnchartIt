from django.http import HttpResponse
from .src.logger import *
from .src.program import *
from .src.checker import *
from .src.interpreter import *
from .src.solver import *
from .src.model import *
from .src.distinguisher import *
from json import load
from os import listdir
import sys
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views.generic.edit import *
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import *
from .forms import *


logger = get_logger("polls")
logger.setLevel("DEBUG")


def index(request):
    latest_question_list = Question.objects.order_by('-publish_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'index.html', context)


def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'detail.html', {'question': question})


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


def create_poll(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = QuestionForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            instance = Question(**form.cleaned_data)
            instance.save()

            instance2 = Choice(id=None, question_text=instance, choice_text= form.cleaned_data['choice_text'])
            instance2.save()
            instance2 = Choice(id=None, question_text=instance, choice_text= form.cleaned_data['choice_text'])
            instance2.save()
            instance2 = Choice(id=None, question_text=instance, choice_text= form.cleaned_data['choice_text'])
            instance2.save()
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/polls')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = QuestionForm()

    return render(request, 'form.html', {'form': form})
