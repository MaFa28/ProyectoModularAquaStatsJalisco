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
    path('domicilio/',views.domicilio, name='domicilio'),
    path('salir/',views.salir, name='salir'),#Url para cerrar sesion
    path('sesion/', views.inicio, name='insesion'),#Url para el inicio de sesion
    path('perfil/', views.perfil, name='perfil'),#Url para el perfil
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #Se agrega para poder agregar las imagenes
