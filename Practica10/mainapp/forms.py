#encoding:utf-8
from django.forms import ModelForm
from django import forms
from mainapp.models import Pelicula
from django.db.models.fields import DateField

class peliculaForm(forms.Form):
    idpeli = forms.IntegerField(label='Introducir ID de película (Números del 1-3364)')
    
class usuarioForm(forms.Form):
    id = forms.IntegerField(label="Introducir el id")
    