from django.shortcuts import render_to_response, redirect
from mainapp.models import Usuario, Ocupacion
from Practica10.settings import BASE_DIR
import mainapp.models as models
import os
from datetime import datetime
from django.utils import timezone

def populate(request):
    occupations = {}
    for line in open(os.path.join(BASE_DIR, "data/u.occupation"), "r"):
        line = line.strip()
        occ = models.Ocupacion.objects.create(nombre=line)
        occupations[line] = occ
    users = {}
    for line in open(os.path.join(BASE_DIR, "data/u.user"), "r"):
        line = line.strip().split('|')
        u = models.Usuario.objects.create(edad=int(line[1]), sexo=line[2], ocupacion=occupations[line[3]], codigopostal=line[4])
        users[int(line[0])] = u
    films = {}
    for line in open(os.path.join(BASE_DIR, "data/u.item"), "r"):
        line = line.strip().decode("cp1252").split('|')
        if line[2]=="":
            line[2]="30-Oct-1996"
        u = models.Pelicula.objects.create(titulo=line[1], fechaestreno=datetime.strptime(line[2], "%d-%b-%Y"), imdburl=line[4])
        films[int(line[0])] = u
    for line in open(os.path.join(BASE_DIR, "data/u.data"), "r"):
        line = line.strip().split('\t')
        models.Puntuacion.objects.create(usuario=users[int(line[0])], pelicula=films[int(line[1])], puntuacion=int(line[2]), momento=timezone.now())
    return redirect('/')

def main(request):
    return render_to_response('main.html')

def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    ocupaciones = Ocupacion.objects.all()
    print usuarios
    print ocupaciones
    return render_to_response('usuarios.html', {'lista':usuarios, 'ocupaciones':ocupaciones})