from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioPersonalizado

# UserAdmin asegura que las contraseñas se encripten correctamente al guardarlas desde la web
admin.site.register(UsuarioPersonalizado, UserAdmin)
