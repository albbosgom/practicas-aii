#encoding:utf-8
from django.forms import ModelForm
from django import forms
from mainapp.models import Pelicula
from django.db.models.fields import DateField

class peliculaForm(forms.Form):
    anhoEstreno = forms.DateField(label='Introducir fecha con formato YYYY-MM-DD')
    
    