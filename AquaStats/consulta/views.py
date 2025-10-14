from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm #importar el form de django
from django.contrib.auth.models import User #metodo para registro de usuarios
from django.contrib.auth import login, logout, authenticate #Metodos de autenticacion
from django.db import IntegrityError #Errores en DB
from django.http import HttpResponse # mensajes en pantalla
from .formdom import RegistroDom, RegistroCosumo #Traer mis formularios
from .models import Foto



# Create your views here.

def home(request):#Vista del Inicio
    fotos = Foto.objects.filter(activo=True)#Pasar el carrusel a la vista
    return render(request, 'inicio.html',{"fotos" : fotos})

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
                if Form.is_valid():
                    nuevo_dom = Form.save(commit=False)
                    nuevo_dom.id_usuario = request.user #Solicta el usuario a la base de datos
                    nuevo_dom.save() #Guarda la informacion en la base datos
                    return redirect('perfil')
                else:
                    return render(request,'domicilio.html',{
                        'form' : RegistroDom,
                        'error' : 'Ingresa datos validos'
                    })
           except Exception as e: #Muestra error en pantalla si no se completan los datos
               return render(request,'domicilio.html',{
                   'form' : RegistroDom,
                   'error' : f'Ocurrio un error'
               })
        
def perfil(request):#Vista perfil
    return render(request,'perfil.html')
            

def reporte(request):#Vista para los  reportes
    if request.method == 'GET': #Regresa la misma vista si se crea nuevo formulario
        return render(request,'reporte.html',{
            'form' : RegistroCosumo
        })
    else: 
        try: #logica para guardar los datos de la  BdD
            form = RegistroCosumo(request.POST)
            if form.is_valid():#Validacion de datos
                nuevo_rep = form.save(commit=False)
                nuevo_rep.id_usuario = request.user #pide a la base datos el usuario
                nuevo_rep.save() #guarda la informacion en la base de datos
                return redirect('perfil') #redirecciona a la otra vista
            else:
                return render(request,'reporte.html',{ #si la condicional no se cumple se regresa el mismo formulario
                    'form' : RegistroCosumo,
                    'error' : 'Ingresa datos validos'
                })
        except Exception as e: #Manejo de errores
            return render(request,'reporte.html',{
                   'form' : RegistroCosumo,
                   'error' : f'Ocurrio un error'
               })
            
    
    