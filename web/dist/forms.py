from django.forms import *
from .models import *
from django.urls import reverse


class InstanceForm(ModelForm):
    file_field = forms.FileField(required=True, widget=ClearableFileInput(attrs={'multiple': True}))
    input_constraints = CharField(required=True)
    interaction_model = CharField(required=True)