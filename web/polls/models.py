from django.db import models
from django.urls import reverse


class Question(models.Model):
    question_text = models.CharField(max_length=200)

    def __str__(self):
        return self.question_text

    def get_absolute_url(self):
        return reverse('polls:index')


class Choice(models.Model):
    question_text = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
