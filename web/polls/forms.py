from django.forms import *
from .models import *
from django.urls import reverse


class QuestionForm(ModelForm):
    question_text = CharField(required=True)
    publish_date = CharField(required=False)
    choice_text = CharField(required=True)

    class Meta():
        model = Question
        fields = ('question_text', 'choice_text')