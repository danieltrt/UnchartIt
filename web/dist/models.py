from django.db import models
from django.urls import reverse


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    interaction_model = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.question_text

    def get_absolute_url(self):
        return reverse('dist:index')


class Choice(models.Model):
    question_text = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    correctness = models.BooleanField(null=True)

    def __str__(self):
        return self.choice_text
