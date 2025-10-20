"""
URL configuration for aquajalisco project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from consulta import views #importando las vistas
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'), #Url del home
    path('registro/', views.sigup, name='sigup'),#Url del registro de usuarios
    path('domicilio/',views.domicilio, name='domicilio'),#Url de crear domicilio
    path('domicilios/',views.ver_domicilios, name='ver_domicilios'),#URL de ver los domicilios registrados
    path('domicilios/editar/<int:domicilio_id>', views.editar_domicilio, name="editar_domicilio"),#URL de editar los domicilios registrados
    path('domicilios/eliminar/<int:domicilio_id>', views.eliminar_domicilio, name='eliminar_domicilio'),#URL de eliminar los domicilios registrados
    path('salir/',views.salir, name='salir'),#Url para cerrar sesion
    path('sesion/', views.inicio, name='insesion'),#Url para el inicio de sesion
    path('perfil/', views.perfil, name='perfil'),#Url para el perfil
    path('crearReporte/',views.reporte, name='reporte'),#Url para los reportes
    path('perfil/editar/<int:id>/', views.editar_reporte, name='editar_reporte'),#URL editar reporte
    path('perfil/eliminar/<int:id>', views.eliminar_reporte, name='eliminar_reporte'),#URL eliminar reporte
    path('perfil/exportar_excel/', views.exportar_excel, name='exportar_excel'),#URL para crear los archivos .xls
    path('perfil/exportar_pdf/', views.exportar_pdf, name='exportar_pdf'),#URL para crear pdf
    path('reportes_todos/', views.reportes_publicos, name='reportes_todos'),#URL para ver todo los reportes
    path('analisis/', views.analisis_usuario, name='analisis_usuario'),#URL para ver un analisis por usuario
    path('dashboard/',views.dashboard_global, name='dashboard_global'),#URL para ver el analis de todos los usuarios
    path('regresion/', views.regresion_lineal, name='regresion'),#URL para aplicar el algoritmo de regresion por usuario
    path('regresion_global/', views.regresion_global, name='regresion_global'),#URL para aplicar el algoritmo de regresion de manera global
    path('historial_metricas/',views.historial_metricas, name='historial_metricas'),#URL para ver las metricas del modelo
    path('bayes/', views.clasificacion_bayes, name='bayes'),#Urle para aplicar el modelo de Bayes
    path('historial_bayes/', views.historial_bayes, name='historial_bayes'),#Url para ver el historial del modeloBayes
    path('reentrenar_bayes/', views.reentrenar_bayes, name='reentrenar_bayes'),#Url para reentrenar el modelo de Bayes
] 

#Se agrega para poder agregar las imagenes
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
