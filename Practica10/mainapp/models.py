from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Ocupacion(models.Model):
    nombre = models.CharField(max_length=13)
    def __unicode__(self):
        return self.nombre

class Usuario(models.Model):
    edad = models.SmallIntegerField()
    sexo = models.CharField(max_length=1)
    ocupacion = models.ForeignKey(Ocupacion)
    codigopostal = models.CharField(max_length=5)

class Categoria(models.Model):
    nombre = models.CharField(max_length=11)
    def __unicode__(self):
        return self.nombre

class Pelicula(models.Model):
    titulo = models.CharField(max_length=128)
    fechaestreno = models.DateField()
    fechavideo = models.DateField(blank=True, null=True)
    imdburl = models.URLField()
    categorias = models.ManyToManyField(Categoria, blank=True)
    def __unicode__(self):
        return self.titulo

class Puntuacion(models.Model):
    usuario = models.ForeignKey(Usuario)
    pelicula = models.ForeignKey(Pelicula)
    puntuacion = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    momento = models.DateTimeField()
    def __unicode__(self):
        return str(self.usuario) + " puntua '" + str(self.pelicula) + "' con " + str(self.puntuacion)
    class Meta:
        unique_together = ("usuario", "pelicula")
