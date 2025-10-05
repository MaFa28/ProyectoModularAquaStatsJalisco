from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm #importar el form de django
from django.contrib.auth.models import User #metodo para registro de usuarios
from django.contrib.auth import login, logout, authenticate #Metodos de autenticacion
from django.db import IntegrityError #Errores en DB
from django.http import HttpResponse # mensajes en pantalla
from .formdom import RegistroDom, consumoagua #Traer mis formularios



# Create your views here.

def home(request):#Vista del Inicio
    return render(request, 'inicio.html')

def sigup(request):#Vista del registro de usuarios
    
    if request.method == 'GET':#Enviando el formulario a pantalla
        return render(request, 'registro.html', {
            'form' : UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:#Verificacion de datos antes de guardar
            try: #manejo de errores
                #registro de usuario
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save() #guardar el usuario en la BD 
                login(request, user)#crea el id de inicio de sesion
                return redirect('domicilio')#envia a la vista domicilio
            except IntegrityError: 
                return render(request, 'registro.html',{ #error por si el usuario ya existe
                    'form' : UserCreationForm,
                    "error" : 'Este usuario ya existe'
                })
        return render(request, 'registro.html', {
            'form' : UserCreationForm,
            "error" : 'Contraseñas incorrectas'
        })

def salir(request):#Vista para cerrar sesion
    logout(request)
    return redirect('home')


def inicio(request):#Vista inicio de sesion
    if request.method == 'GET':#Renvio del formulario
        return render(request, 'insesion.html', {
            'form' : AuthenticationForm
        })
    else:#Metodo para revisar que el usuario exista
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None: #Revisar si la contraseña o usuario existen
            return render(request,'insesion.html', {
                'form' : AuthenticationForm,
                'error' : 'Usuario o contraseña incorrecta'
            })
        else: 
            login(request, user)#Usuario existente
            return redirect('perfil')
    

def domicilio(request):#Vista de registro de domicilio
       if request.method == 'GET':#Si la peticion en GET regresa el formulario
           return render(request,'domicilio.html',{
               'form' : RegistroDom
           })
       else:
           try:#logica para guardar los datos en la Base de Datos
                Form = RegistroDom(request.POST)
                nuevo_dom = Form.save(commit=False)
                nuevo_dom.id_usuario = request.user
                nuevo_dom.save()
                return redirect('perfil')
           except ValueError: #Muestra error en pantalla si no se completan los datos
               return render(request,'domicilio.html',{
                   'form' : RegistroDom,
                   'error' : 'Ingresa datos validos'
               })
        
           
       

def perfil(request):#Vista perfil
    return render(request,'perfil.html')
            
            
    