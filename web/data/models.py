from django.db import models


class Chart(models.Model):
    file_name = models.CharField(max_length=200)

    def __str__(self):
        return self.file_name


# Create your models here.
