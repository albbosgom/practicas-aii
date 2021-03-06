# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, redirect
from mainapp.models import Usuario, Ocupacion, Pelicula, Puntuacion
from mainapp.forms import peliculaForm, usuarioForm
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.core.mail import EmailMessage
from Practica10.settings import BASE_DIR
import mainapp.models as models
import os
import recommendations
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

def lista_peliculas(request, p, r):
    return render_to_response('peliculas.html', {'pelicula':p, 'similar':r})

def pelicula(request):
    if request.method=='POST':
        formulario = peliculaForm(request.POST)
        if formulario.is_valid():
            # Cogemos la película de la que queremos recomendaciones
            pelicula = Pelicula.objects.get(id = formulario.cleaned_data['idpeli'])
            usuarios = Usuario.objects.all()
            puntuaciones = {}
            #En este for metemos en puntuaciones todas las puntuaciones siguiendo el formato de "critics" en recommendations.py
            for user in usuarios:
                puntuacions = Puntuacion.objects.filter(usuario = user)
                pelis = {}
                for puntuacion in puntuacions:
                    pelis[puntuacion.pelicula.titulo] = puntuacion.puntuacion
                puntuaciones[user.id] = pelis
            #Una vez en el formato, simplemente calculamos los 3 más similares
            similar = recommendations.calculateSimilarItems(puntuaciones, 3)
            #Y ahora cogemos las recomendaciones de la película que queremos
            res = similar[pelicula.titulo]
            #Y las pasamos por parámetro
            recomen= [res[0][1],res[1][1],res[2][1]]                         
            return lista_peliculas(request,pelicula, recomen)
    else:
        formulario = peliculaForm()
    return render_to_response('peliculaForm.html', {'formulario':formulario}, context_instance=RequestContext(request))

def lista_usuarios(request, usuario):
    peliculas={}
    puntuaciones = Puntuacion.objects.filter(usuario = usuario)
    
    return render_to_response('usuarios.html', {'lista':puntuaciones})

def usuario(request):
    if request.method=='POST':
        formulario = usuarioForm(request.POST)
        if formulario.is_valid():
            usuario = Usuario.objects.filter(id = formulario.cleaned_data['id'])
            return lista_usuarios(request,usuario)
    else:
        formulario = usuarioForm()
    return render_to_response('usuarioForm.html', {'formulario':formulario}, context_instance=RequestContext(request))

def similaridad(a,b,pmap,pavg):
    from math import sqrt
    usuarios = []
    for usu in pmap:
        p = pmap[usu]
        if (a in p) and (b in p):
            usuarios.append(usu)
    if not usuarios:
        return 0
    num,denA,denB = 0,0,0
    for usu in usuarios:
        rU = pavg[usu]
        rA = pmap[usu][a]
        rB = pmap[usu][b]
        num += (rA-rU)*(rB-rU)
        denA += (rA-rU)*(rA-rU)
        denB += (rB-rU)*(rB-rU)
    if denA==0 or denB==0:
        return 0
    return num / sqrt(denA*denB)

def recomienda_pelis(usuario,N=2):
    todoPelis = {}
    pmap,pavg,pcnt = {}, {}, {}
    usuario_id = usuario.id
    for puntu in Puntuacion.objects.all():
        pid = puntu.usuario.id
        pel = puntu.pelicula.titulo
        if pel not in todoPelis:
            todoPelis[pel] = False
        if pid==usuario_id:
            todoPelis[pel] = True
        pun = puntu.puntuacion
        if pid not in pmap:
            mapp = {}
            pmap[pid] = mapp
            pavg[pid] = 0
            pcnt[pid] = 1
        else:
            mapp = pmap[pid]
            pavg[pid] += float(pun)
            pcnt[pid] += 1
        mapp[pel] = pun
    for k in pavg:
        pavg[k] /= pcnt[k]
    print pavg
    la = []
    for peli in todoPelis:
        if todoPelis[peli]:
            continue
        num,den = 0,0
        for punt in todoPelis:
            if not todoPelis[punt]:
                continue
            sim = similaridad(peli,punt,pmap,pavg)
            rat = pmap[usuario_id][punt]
            num += sim*rat
            den += sim
            print sim,rat
        if den==0:
            continue
        la.append((num/den,peli))
    la.sort(reverse=True)
    return la[0:N]

def vista_recomienda_pelis(request, usuario):
    pelis = recomienda_pelis(usuario)
    return render_to_response('pelisrec.html', {'pelis':pelis})

def pelis_recomendadas(request):
    if request.method=='POST':
        formulario = usuarioForm(request.POST)
        if formulario.is_valid():
            usuario = Usuario.objects.get(id = formulario.cleaned_data['id'])
            return vista_recomienda_pelis(request, usuario)
    else:
        formulario = usuarioForm()
    return render_to_response('usuarioForm.html', {'formulario':formulario}, context_instance=RequestContext(request))