from django.contrib import admin
from .models import domicilior, recomendaciones, consumoagua

# Register your models here.
#Registro de modelos para la vista de administrador
admin.site.register(domicilior)
admin.site.register(recomendaciones)
admin.site.register(consumoagua)
