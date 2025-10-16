from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm #importar el form de django
from django.contrib.auth.models import User #metodo para registro de usuarios
from django.contrib.auth import login, logout, authenticate #Metodos de autenticacion
from django.db import IntegrityError #Errores en DB
from django.http import HttpResponse, FileResponse # mensajes en pantalla
from .formdom import RegistroDom, RegistroCosumo #Traer mis formularios
from .models import Foto, consumoagua #Traer mis modelos
from django.core.paginator import Paginator #Agregar paginacion en la tabla
import openpyxl#Para trabajar con archivos de excel
import io #Trabajar con los PDF
from datetime import datetime #para convertir la informacion para exportar
from reportlab.pdfgen import canvas#Crear PDF
from reportlab.lib.pagesizes import letter#Crear PDF
from reportlab.lib import colors#Crear PDF
from reportlab.lib.units import inch#Crear PDF
from django.utils import timezone




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
        form = UserCreationForm
        if form.is_valid():#Verificacion de datos antes de guardar
            try: #manejo de errores
                #registro de usuario
                user = form.save()#Guarda el usuario en la BDD
                login(request, user)#crea el id de inicio de sesion
                return redirect('domicilio')#envia a la vista domicilio
            except IntegrityError: 
                return render(request, 'registro.html',{ #error por si el usuario ya existe
                    'form' : UserCreationForm,
                    "error" : 'Este usuario ya existe'
                })
        else:
            return render(request, 'registro.html', {
            'form' : UserCreationForm,
            "error" : 'Existen errores en el formulario'
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
    
    #Filtros
    tipo = request.GET.get('tipo')
    fecha = request.GET.get('fecha')
    
    #Filtrado de reportes del usuario logeado
    reportes = consumoagua.objects.filter(id_usuario=request.user)
    
    if tipo:
        reportes = reportes.filter(tipo_reporte=tipo)
    if fecha:
        reportes = reportes.filter(fecha=fecha)
        
    reportes = reportes.order_by('-fecha')
    
    #Paginacion
    paginator = Paginator(reportes, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request,'perfil.html',{
        'page_obj' : page_obj,#Elementos que se mandan a la vista
        'tipo' : tipo,
        'fecha' : fecha,
    })
            
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
            

def exportar_excel(request):#Vista para exportar archivos a EXCEl
    #Filtros
    tipo = request.GET.get('tipo')
    fecha = request.GET.get('fecha')
    
    reportes = consumoagua.objects.filter(id_usuario=request.user)
    if tipo:
        reportes = reportes.filter(tipo_reporte=tipo)
    if fecha:
        try:#Convertir la fecha antes de filtrar
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
            reportes = reportes.filter(fecha=fecha_obj)
        except:
            pass #Ignora el formato
    
    #Crear el libro de excel 
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reportes Consumo de Agua"
    
    #Agregar encabezado
    ws.append(["Cantidad M3", "Tipo reporte", "Fecha", "Domicilio"])
    
    #Insertar filas
    for r in reportes:
        ws.append([
            r.cantidad,
            r.get_tipo_reporte_display(),
            r.fecha.strftime("%d/%m/%Y"),
            r.id_domicilio.direccion,
        ])
    
    #Respuesta HTTP
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",)
    response["Content-Disposition"] = 'attachment; filename="reportes_consumo.xlsx"'
    wb.save(response)
    return response


def exportar_pdf(request):#Vista para generar PDF con estilos
    tipo = request.GET.get('tipo')
    fecha = request.GET.get('fecha')
    
    reportes = consumoagua.objects.filter(id_usuario=request.user)
    
    if tipo:
        reportes = reportes.filter(tipo_reporte=tipo)
    if fecha:
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
            reportes = reportes.filter(fecha=fecha_obj)
        except ValueError:
            pass#Ignora el formato
        
    #Se crea buffer temporal
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    #Titulo
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 50, "Reporte Consumo de Agua")
    
    #Encabezados, donde se añade colores, fecha y usuario que genero
    p.setFillColor(colors.HexColor("#0077b6"))
    p.rect(0, height - 80, width, 80, fill=True)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 50, "Reporte de Consumo de Agua")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 65, f"Usuario: {request.user.username}")
    p.drawString(width - 180, height - 65, f"Generado: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    
    y = height - 120
    p.setFont("Helvetica-Bold", 12)
    p.setFillColor(colors.black)
    p.drawString(50, y, "Cantidad (m³)")
    p.drawString(150, y, "Tipo")
    p.drawString(250, y, "Fecha")
    p.drawString(350, y, "Domicilio")
    
    #Filas
    y -= 20
    p.setFont("Helvetica", 10)
    for r in reportes:
        if y < 80:  # Nueva página
            p.showPage()
            y = height - 80
        p.drawString(50, y, str(r.cantidad))
        p.drawString(150, y, r.get_tipo_reporte_display())
        p.drawString(250, y, r.fecha.strftime("%d/%m/%Y"))
        p.drawString(350, y, r.id_domicilio.direccion[:40])
        y -= 20
            
    p.showPage()
    p.save()#Guarda el PDF
    buffer.seek(0)
    
    return FileResponse(buffer, as_attachment=True, filename="reportes_consumo.pdf")