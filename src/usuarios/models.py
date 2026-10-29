
from django.contrib.auth.models import AbstractUser
from django.db import models

class UsuarioPersonalizado(AbstractUser):
    # Django ya incluye username, password, email, first_name, last_name
    
    # Añade tus campos extra aquí
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    direccionCasa = models.CharField(max_length=255, blank=True, null=True)
    direccionTrabajo = models.CharField(max_length=255, blank=True, null=True)
    direccionOtro = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.username