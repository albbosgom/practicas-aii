from django.shortcuts import render_to_response
from mainapp.models import Pelicula
from mainapp.forms import peliculaForm
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.core.mail import EmailMessage

def main(request):
    return render_to_response('main.html')


def lista_peliculas(request, p):
    return render_to_response('peliculas.html', {'lista':p})

def pelicula(request):
    if request.method=='POST':
        formulario = peliculaForm(request.POST)
        if formulario.is_valid():
            pelis = Pelicula.objects.filter(fechaestreno = formulario.cleaned_data['anhoEstreno'])
            return lista_peliculas(request,pelis)
    else:
        formulario = peliculaForm()
    return render_to_response('peliculaForm.html', {'formulario':formulario}, context_instance=RequestContext(request))