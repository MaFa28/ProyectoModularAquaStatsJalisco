from django.contrib import admin
from .models import domicilior, recomendaciones, consumoagua, Foto
from django.utils.html import format_html
# Register your models here.
#Registro de modelos para la vista de administrador
admin.site.register(domicilior)
admin.site.register(recomendaciones)
admin.site.register(consumoagua)
admin.site.register(Foto)

#Modelo para las fotos
class FotoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "descripcion" , "imagen_previa")
    list_editable = ("orden", "activo")
    search_fields = ("titulo", "descripcion")
    list_filter = ("activo",)
    ordering = ("orden",)
    def imagen_pre(self, obj):
        
        if obj.imagen:
            return format_html('<img src="{}" width="100" height="60" style="object-fit: cover; border-radius:5px"/>', obj.imagen.url)
        return "Sin imagen"
    
    imagen_pre.allow_tags = True
    imagen_pre.short_description = "Vista previa"