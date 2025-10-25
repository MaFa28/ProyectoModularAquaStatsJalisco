#Metodo de ayuda para guardar las recomendaciones
from django.utils import timezone
from consulta.models import recomendaciones

def guardar_recomendacion(user, texto, algoritmo, fecha=None):
    if fecha is None:
        fecha = timezone.now().date()
    obj, _ = recomendaciones.objects.update_or_create(
        id_usuario=user,
        algoritmo=algoritmo,
        fecha=fecha,
        defaults={'texto': texto},
    )
    return obj
