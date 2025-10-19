from django.shortcuts import render, redirect, get_object_or_404#Obtiene los datos de la BDD si no existen arroja error
from django.contrib import messages #Enviar mensajes temporales al usuario
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm #importar el form de django
from django.contrib.auth.models import User #metodo para registro de usuarios
from django.contrib.auth import login, logout, authenticate #Metodos de autenticacion
from django.contrib.auth.decorators import login_required#Proteger las rutas
from django.db import IntegrityError #Errores en DB
from django.http import HttpResponse, FileResponse # mensajes en pantalla
from .formdom import RegistroDom, RegistroCosumo #Traer mis formularios
from .models import Foto, consumoagua, domicilior, RegresionMetricas, ClasificacionBayes, EntrenamientoBayes #Traer mis modelos
from django.core.paginator import Paginator #Agregar paginacion en la tabla
import openpyxl#Para trabajar con archivos de excel
import io  #Trabajar con los PDF
from io import BytesIO
import pandas as pd #Manejo de datos
import numpy as np#Manejo de datos y los muestra en graficas
import json #Utilizar instrucciones Javascript
import plotly.express as px #Manejo de datos y muestra datos en dashboard
import plotly.io as pio
from datetime import datetime #para convertir la informacion para exportar
from reportlab.pdfgen import canvas#Crear PDF
from reportlab.lib.pagesizes import letter#Crear PDF
from reportlab.lib import colors#Crear PDF
from reportlab.lib.units import inch#Crear PDF
from django.utils import timezone #manejo de fechas y horas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle #Estilos en el PDF
from reportlab.lib.styles import getSampleStyleSheet #Trabajo en PDF
from sklearn.linear_model import LinearRegression #Trae el algoritmo de Regresion lineal
from sklearn.metrics import mean_squared_error, r2_score #Auxiliares para los algoritmos
from sklearn.naive_bayes import GaussianNB #Trae el algoritmo de Bayes
from sklearn.preprocessing import StandardScaler #Auxiliar de los algoritmos




# Create your views here.

def home(request):#Vista del Inicio
    fotos = Foto.objects.filter(activo=True)#Pasar el carrusel a la vista
    return render(request, 'inicio.html',{"fotos" : fotos})

def sigup(request):#Vista del registro de usuarios
    if request.method == 'GET':#Enviando el formulario a pantalla
        return render(request,'registro.html',{
            'form' : UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:#Verificacion de datos antes de guardar
            try:#manejo de errores
                #registro de usuario
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()#guardar el usuario en la BD
                login(request,user)#crea el id de inicio de sesion
                return redirect('domicilio')#envia a la vista domicilio
            except IntegrityError:
                return render(request,'registro.html',{#error por si el usuario ya existe
                    'form' : UserCreationForm,
                    "error" : 'Usuario ya existe'
                })
        return render(request,'registro.html',{
            'form' : UserCreationForm,
            "error" : 'Corrige los errores'
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
                    return redirect('ver_domicilios')
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
   

def ver_domicilios(request):#Vista para ver los domicilios registrados
    domicilios = domicilior.objects.filter(id_usuario=request.user) #Filtrado de domicilios del usuario logeado
    return render(request, 'domicilios.html',{
        'domicilios' : domicilios
    })   

def editar_domicilio(request, domicilio_id):
    domicilio = get_object_or_404(domicilior, id=domicilio_id, id_usuario=request.user) #Metodo para evitar que otros usuarios modifiquen formularios que no sean suyos
    
    if request.method == 'POST':#Metodo POST
        form = RegistroDom(request.POST, instance=domicilio)
        if form.is_valid():#Revisa si la informacion es valida
            form.save()#Guarda la informacion
            return redirect('ver_domicilios')#redirecciona a la vista
    else:#Si no se cumple la condicion regresa el form otra vez
        form = RegistroDom(instance=domicilio)#Si no se cumple la condicion regresa el form otra vez
    return render(request,'editardomi.html',{
        'form' : form
    })
     
def eliminar_domicilio(request, domicilio_id):
    domicilio = get_object_or_404(domicilior, id=domicilio_id, id_usuario=request.user)#Si no se cumple la condicion regresa el form otra vez
    
    if request.method == 'POST':#Metodo POST
        domicilio.delete()#Elimina el domicilio de la base de datos
        return redirect('ver_domicilios')#Redirecciona a los domicilios
    
    return render(request, 'eliminardomi.html', { #Regresa el mismo formulario a pantalla
        'domicilio': domicilio
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
            
def editar_reporte(request, id):#Vista para editar los reportes
    reporte = get_object_or_404(consumoagua, id=id, id_usuario=request.user)#Metodo para evitar que otros usuarios modifiquen formularios que no sean suyos
    
    
    if request.method == 'POST':
        form = RegistroCosumo(request.POST, instance=reporte)
        if form.is_valid():#Valida si el formulario es valido
            form.save()#Metodo que guarda la informacion 
            messages.success(request, 'Reporte Actualizado')
            return redirect('perfil')
        else:
            messages.error(request, 'Error al Actualizar')#Mensaje de error
    else:
        form = RegistroCosumo(instance=reporte)
    return render(request,'editarrepo.html',{
        'form' : form
    })
    
def eliminar_reporte(request, id):#Vista para eliminar los reportes
    reporte = get_object_or_404(consumoagua, id=id, id_usuario=request.user)#Metodo para evitar que otros usuarios eliminen formularios que no sean suyos
    
    if request.method == 'POST':
            reporte.delete()#Metodo para eliminar el reporte
            messages.success(request, 'Reporte eliminado')
            return redirect('perfil')
    return render(request, 'eliminarrepo.html',{
        'reporte' : reporte
    })

def exportar_excel(request):#Vista para exportar archivos a EXCEl
    #Filtros
    tipo = request.GET.get('tipo')
    fecha = request.GET.get('fecha')
    
    reportes = consumoagua.objects.filter(id_usuario=request.user) #Obtiene los datos del usuario logeado
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
    
    reportes = consumoagua.objects.filter(id_usuario=request.user)#Se obtienen solos los datos del usuario logeado
    
    #Filtros
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
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=40, rightMargin=40, topMargin=60, bottomMargin=40  # 👈 márgenes
    )

    styles = getSampleStyleSheet()
    elements = []

    #Encabezado principal
    titulo = Paragraph("<b>Reporte Público de Consumo de Agua</b>", styles["Title"])
    fecha_gen = Paragraph(f"<b>Generado:</b> {timezone.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"])
    elements.append(titulo)
    elements.append(Spacer(1, 10))
    elements.append(fecha_gen)
    elements.append(Spacer(1, 20))

    #Encabezados de tabla
    data = [["Usuario", "Consumo (m3)", "Tipo de reporte", "Domicilio", "Fecha"]]

    #Filas
    for r in reportes:
        data.append([
            r.id_usuario.username,
            str(r.cantidad),
            r.get_tipo_reporte_display(),
            r.id_domicilio.direccion,
            r.fecha.strftime("%d/%m/%Y"),
        ])

    #Crear tabla con estilos y márgenes
    table = Table(data, colWidths=[100, 80, 100, 120, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0077b6")),  #encabezado azul
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  #bordes de tabla
        ('LEFTPADDING', (0, 0), (-1, -1), 6),          #margen interno
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    
    return FileResponse(buffer, as_attachment=True, filename="reportes_consumo.pdf")

def reportes_publicos(request):#Vista para vizualizar todos los reportes de manera global
    reportes = consumoagua.objects.select_related('id_usuario','id_domicilio')
    
    #Filtros
    tipo_reporte = request.GET.get('tipo_reporte')
    region = request.GET.get('region')
    usuario = request.GET.get('usuario')
    
    if tipo_reporte:#Validaciones para los filtros
        reportes = reportes.filter(tipo_reporte=tipo_reporte)
    if region:
        reportes = reportes.filter(id_domicilio__region=region)
    if usuario: 
        reportes= reportes.filter(id_usuario__username__icontains=usuario)
        
    #Metodo para exportar todo o la pagina actual
    if 'exportar_excel' in request.GET or 'exportar_pdf' in request.GET:
        exportar_todo = request.GET.get('exportar_todo', '0') == '1'

    #Exportar solo la página actual
    exportar_todo = request.GET.get('exportar_todo', False)
    if not exportar_todo:
        paginator = Paginator(reportes, 10)
        page_number = request.GET.get('page')
        reportes = paginator.get_page(page_number).object_list

    data = [#Obtiene la informacion
        {
            'Usuario': r.id_usuario.username,
            'Consumo (m3)': r.cantidad,
            'Región': r.id_domicilio.region,
            'Tipo de Reporte': r.get_tipo_reporte_display(),
        }
        for r in reportes
    ]
    
    #Exportar con excel
    if 'exportar_excel' in request.GET:
        df = pd.DataFrame(data)
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        nombre = "reportes_todos.xlsx" if exportar_todo else "reportes_pagina.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{nombre}"'
        df.to_excel(response, index=False)
        return response
    
    
    #Paginacion
    paginator = Paginator(reportes, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'reportes_publicos.html', {
        'page_obj': page_obj,
        'reportes': page_obj.object_list,
    })
    
def analisis_usuario(request):#Vista para ver un remusen del consumo, en forma de tabla y grafica, ademas muestra anomalias
    reportes = consumoagua.objects.filter(id_usuario=request.user).select_related('id_domicilio')#Obtiene solo los reportes de el usuario logeado

    if not reportes.exists():#Verifica que existan reportes
        return render(request, 'analisis_usuario.html', {'mensaje': 'No hay registros de consumo disponibles.'})
    #Covertir los datos a un dataframe
    data = []
    for r in reportes:
        data.append({
            'fecha': r.fecha or timezone.now().date(),
            'cantidad': float(r.cantidad or 0),
            'region': getattr(r.id_domicilio, 'region', '—'),
            'domicilio': getattr(r.id_domicilio, 'direccion', '—'),
        })
    #Formatp para las fechas
    df = pd.DataFrame(data)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['mes'] = df['fecha'].dt.to_period('M')
    #Calculo de metricas
    promedio = df['cantidad'].mean()
    desviacion = df['cantidad'].std()
    maximo = df['cantidad'].max()
    minimo = df['cantidad'].min()


    # Detectar consumos anormales
    df['anormal'] = np.where(
        (df['cantidad'] > promedio + 2*desviacion) | (df['cantidad'] < promedio - 2*desviacion),
        True, False
    )

    #Agrupar por mes
    tendencia = df.groupby('mes')['cantidad'].mean().reset_index()

    #Generar alertas
    alertas = []
    if len(tendencia) > 1:
        tendencia = tendencia.sort_values(by='mes')
        for i in range(1, len(tendencia)):
            mes_actual = tendencia.iloc[i]
            mes_anterior = tendencia.iloc[i - 1]
            if mes_anterior['cantidad'] != 0:
                cambio = ((mes_actual['cantidad'] - mes_anterior['cantidad']) / mes_anterior['cantidad']) * 100
                if cambio > 30:
                    alertas.append({'tipo': 'aumento', 'mensaje': f" Tu consumo aumentó un {cambio:.1f}% en {mes_actual['mes']} respecto al mes anterior."})
                elif cambio < -30:
                    alertas.append({'tipo': 'disminucion', 'mensaje': f" Tu consumo disminuyó un {abs(cambio):.1f}% en {mes_actual['mes']} respecto al mes anterior."})

    #Una vez obtenida la informacion esta se agrupa y se envia a la vista
    contexto = {
            'promedio': round(promedio, 2),
            'desviacion': round(desviacion, 2),
            'maximo': maximo,
            'minimo': minimo,
            'anormales': df[df['anormal'] == True].to_dict(orient='records'),
            'tendencia': tendencia.to_dict(orient='records'),
            'alertas': alertas,
            'total_registros': len(df),
            'fecha_actual': timezone.now(),
        }

    
    return render(request, 'analisis_usuario.html', contexto)
           
def dashboard_global(request):#Vista para ver datos de manera global de todos los usuarios

    # --- Filtros ---
    tipo = request.GET.get('tipo')
    region = request.GET.get('region')
    usuario = request.GET.get('usuario')

    reportes = consumoagua.objects.select_related('id_domicilio', 'id_usuario')

    if tipo:
        reportes = reportes.filter(tipo_reporte=tipo)
    if region:
        reportes = reportes.filter(id_domicilio__region=region)
    if usuario:
        reportes = reportes.filter(id_usuario__username=usuario)

    # --- Convertir a DataFrame ---
    df = pd.DataFrame(list(reportes.values(
        'fecha',
        'cantidad',
        'tipo_reporte',
        'id_usuario__username',
        'id_domicilio__region'
    )))

    # --- Renombrar columnas ---
    df.rename(columns={
        'id_usuario__username': 'Usuario',
        'id_domicilio__region': 'Region',
        'tipo_reporte': 'Tipo de Reporte',
        'cantidad': 'Cantidad',
        'fecha': 'Fecha'
    }, inplace=True)

    if df.empty:
        return render(request, 'dashboard.html', {'empty': True})

    # --- Preparar datos ---
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['mes_num'] = df['Fecha'].dt.month
    df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce')
    df.dropna(subset=['Cantidad'], inplace=True)

    # --- Gráficas principales ---
    graf1 = px.line(df, x='Fecha', y='Cantidad', color='Usuario', title='Tendencia de Consumo por Usuario')
    graf2 = px.bar(df.groupby(['Usuario', 'Tipo de Reporte'])['Cantidad']
                   .mean().reset_index(),
                   x='Usuario', y='Cantidad', color='Tipo de Reporte',
                   title='Promedio por Usuario y Tipo de Reporte')
    graf3 = px.pie(df, names='Region', title='Distribución por Región')
    graf4 = px.box(df, x='Usuario', y='Cantidad', title='Distribución del Consumo por Usuario')

    # --- Contexto para el template ---
    context = {
        'graf1': graf1.to_json(),
        'graf2': graf2.to_json(),
        'graf3': graf3.to_json(),
        'graf4': graf4.to_json(),
    }

    return render(request, 'dashboard.html', context)

def procesar_regresion(reportes, usuario=None):#Vista que procesa los datos para guardar en la base de datos
    #Recibe y procesa los datos antes de guardar en la base datos
    df = pd.DataFrame(list(reportes.values('fecha', 'cantidad')))
    if df.empty:
        return None

    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce')
    df = df.dropna(subset=['fecha', 'cantidad'])
    df = df[df['cantidad'] > 0]
    if df.empty:
        return None

    df['mes_num'] = df['fecha'].dt.month
    df_mes = df.groupby('mes_num', as_index=False)['cantidad'].mean().sort_values('mes_num')
    if len(df_mes) < 2:
        return None

    X = df_mes[['mes_num']]
    y = df_mes['cantidad']

    modelo = LinearRegression()
    modelo.fit(X, y)
    y_pred = modelo.predict(X)

    r2 = r2_score(y, y_pred)
    mse = mean_squared_error(y, y_pred)
    b0 = modelo.intercept_
    b1 = modelo.coef_[0]
    prediccion = modelo.predict([[X['mes_num'].max() + 1]])[0]

    # Guarda las metricas automaticamente
    RegresionMetricas.objects.create(
        usuario=usuario,
        r2=r2,
        mse=mse,
        b0=b0,
        b1=b1,
        prediccion=prediccion
    )
    #Retorna los elementos listos
    return {
        'r2': round(r2, 3),
        'mse': round(mse, 2),
        'b0': round(b0, 3),
        'b1': round(b1, 3),
        'prediccion': round(prediccion, 2),
        'datos': df_mes.to_dict(orient='records')
    }

def regresion_lineal(request):#Vista que aplica el algoritmo de regresion lineal a un solo usuario
    #Obtiene los datos desde la base de datos
    reportes = consumoagua.objects.filter(id_usuario=request.user).select_related('id_domicilio')
    df = pd.DataFrame(list(reportes.values('fecha', 'cantidad')))

    if df.empty:
        return render(request, 'regresion.html', {'empty': True})

    #Limpia los  datos
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce')
    df = df.dropna(subset=['fecha', 'cantidad'])
    df = df[df['cantidad'] > 0]

    if df.empty:
        return render(request, 'regresion.html', {'empty': True})

    #Agrupa por mes
    df['mes_num'] = df['fecha'].dt.month
    df_mes = df.groupby('mes_num', as_index=False)['cantidad'].mean()

    if len(df_mes) < 2:
        return render(request, 'regresion.html', {
            'empty': True,
            'mensaje': 'Se necesitan al menos 2 meses de datos para la regresión.'
        })

    #Prepara las variables para el modelo
    X = df_mes[['mes_num']]
    y = df_mes['cantidad']

    #Entrena a el modelo
    modelo = LinearRegression()
    modelo.fit(X, y)

    #Calcula predicciones y metricas
    y_pred = modelo.predict(X)
    r2 = r2_score(y, y_pred)
    mse = mean_squared_error(y, y_pred)

    #Obtiene los coeficientes del modelo
    b0 = modelo.intercept_      # Intercepto (β₀)
    b1 = modelo.coef_[0]        # Pendiente (β₁)

    #Calcula las predicciones para el siguiente mes
    mes_siguiente = X['mes_num'].max() + 1
    prediccion_futura = modelo.predict([[mes_siguiente]])[0]
    
    usuario_data = procesar_regresion(reportes, request.user)

    #Prepara los datos para la vista
    context = {
        'r2': round(r2, 3),
        'mse': round(mse, 2),
        'prediccion': round(prediccion_futura, 2),
        'b0': round(b0, 3),
        'b1': round(b1, 3),
        'datos': df_mes.to_dict(orient='records'),
        'usuario': usuario_data,
        'explicacion': (
            "Se aplicó un modelo de regresion lineal simple para estimar la tendencia del consumo "
            "mensual de agua. El modelo ajusta una linea recta a los valores promedio por mes, "
            "evaluando su precision mediante el coeficiente de determinacion (R²) y el error cuadratico medio (MSE). "
            "Finalmente, se realizó una predicción para el siguiente mes basada en la tendencia calculada."
        )
    }

    #Lo envia a el template
    return render(request, 'regresion.html', context)

def regresion_global(request):#Vista que aplica el algoritmo de regresion lineal para todos los usuarios
    #Obtiene los datos desde la base de datos
    reportes = consumoagua.objects.all()
    df = pd.DataFrame(list(reportes.values('fecha', 'cantidad')))

    if df.empty:
        return render(request, 'regresion_global.html', {'empty': True})

    #Realiza Limpieza de datos
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce')
    df = df.dropna(subset=['fecha', 'cantidad'])
    df = df[df['cantidad'] > 0]

    if df.empty:
        return render(request, 'regresion_global.html', {'empty': True})

    # Agrupaciones por mes
    df['mes_num'] = df['fecha'].dt.month
    df_mes = df.groupby('mes_num', as_index=False)['cantidad'].mean()

    if len(df_mes) < 2:
        return render(request, 'regresion_global.html', {
            'empty': True,
            'mensaje': 'Se necesitan al menos 2 meses de datos para la regresión.'
        })

    # Prepara las variables para el modelo
    X = df_mes[['mes_num']]
    y = df_mes['cantidad']

    #Entrenamiento del modelo
    modelo = LinearRegression()
    modelo.fit(X, y)

    # Calcula predicciones y metricas
    y_pred = modelo.predict(X)
    r2 = r2_score(y, y_pred)
    mse = mean_squared_error(y, y_pred)

    #Obtiene coeficientes del modelo
    b0 = modelo.intercept_      # Intercepto (β₀)
    b1 = modelo.coef_[0]        # Pendiente (β₁)

    #Calcula las predicciones para el siguiente mes
    mes_siguiente = X['mes_num'].max() + 1
    prediccion_futura = modelo.predict([[mes_siguiente]])[0]
    
    global_data = procesar_regresion(reportes, None)

    #Prepara los datos para la vista
    context = {
        'r2': round(r2, 3),
        'mse': round(mse, 2),
        'prediccion': round(prediccion_futura, 2),
        'b0': round(b0, 3),
        'b1': round(b1, 3),
        'datos': df_mes.to_dict(orient='records'),
        'global': global_data,
        'explicacion': (
            "Se aplicó un modelo de regresion lineal simple para estimar la tendencia del consumo "
            "mensual de agua. El modelo ajusta una linea recta a los valores promedio por mes, "
            "evaluando su precision mediante el coeficiente de determinacion (R²) y el error cuadratico medio (MSE). "
            "Finalmente, se realizo una prediccion para el siguiente mes basada en la tendencia calculada."
        )
    }

    #Lo envia a el template
    return render(request, 'regresion_global.html', context)

def historial_metricas(request):#Vista para ver las metricas
    metricas = RegresionMetricas.objects.filter(usuario=request.user).order_by('-fecha_entrenamiento')
    return render(request, 'historial_metricas.html', {'metricas': metricas})

def reentrenar_bayes(request):#Vista para que el usuario reentrene al modelo
    #Permite reentrenar manualmente el modelo Naive Bayes
    if request.method == 'POST':
        usuario = request.user

        #Obteniene los datos del usuario
        reportes = consumoagua.objects.select_related('id_usuario').filter(id_usuario=usuario)
        df = pd.DataFrame(list(reportes.values('cantidad')))

        if df.empty:
            messages.warning(request, 'No hay datos suficientes para reentrenar el modelo.')
            return redirect('bayes')

        #Entrenamiento del modelo
        df['categoria'] = pd.qcut(df['cantidad'], q=3, labels=['Bajo', 'Medio', 'Alto'])
        X = df[['cantidad']].values
        y = df['categoria'].values

        modelo = GaussianNB()
        modelo.fit(X, y)

        # Guardar la nueva fecha de entrenamiento
        EntrenamientoBayes.objects.create(usuario=usuario, fecha_entrenamiento=datetime.now())

        #Guarda las clasificaciones actualizadas
        ClasificacionBayes.objects.filter(usuario=usuario).delete()
        for valor, clase in zip(X.flatten(), y):
            ClasificacionBayes.objects.create(usuario=usuario, consumo=valor, categoria=clase)
        #Mensaje si el modelo se actualizo correctamente
        messages.success(request, 'El modelo Bayesiano fue reentrenado correctamente.')
        return redirect('bayes')

def clasificacion_bayes(request):#Vista con la logica necesaria para ejecutar el modelo de Bayes
    usuario = request.user  # revisa credendicales del usuario 
    reportes = consumoagua.objects.select_related('id_domicilio', 'id_usuario').filter(id_usuario=usuario)

    df = pd.DataFrame(list(reportes.values('cantidad', 'id_usuario__username', 'id_domicilio__region')))
    if df.empty:
        return render(request, 'bayes.html', {'empty': True})

    #Prepara los datos
    df['categoria'] = pd.qcut(df['cantidad'], q=3, labels=['Bajo', 'Medio', 'Alto'])
    X = df[['cantidad']].values
    y = df['categoria'].values

    # Realiza una escala de  valores
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    #Entrenamiento del  modelo
    modelo = GaussianNB()
    modelo.fit(X_scaled, y)

    #Prediccion para los nuevos valores
    nuevos = np.array([[10], [50], [100], [500], [1000]])
    nuevos_scaled = scaler.transform(nuevos)
    predicciones = modelo.predict(nuevos_scaled)

    resultados = list(zip(nuevos.flatten(), predicciones))

    #Guarda las predicciones en la base de datos
    for valor, categoria in resultados:
        ClasificacionBayes.objects.create(
            usuario=usuario,
            consumo=valor,
            categoria=categoria
        )

    #Realiza un Conteo distribuciones
    conteo = df['categoria'].value_counts().reset_index()
    conteo.columns = ['Nivel', 'Cantidad']
    #Se aplica el reentrenamiento
    ultima_fecha = EntrenamientoBayes.objects.filter(usuario=usuario).order_by('-fecha_entrenamiento').first()

    #Envia los datos al template
    context = {
        'conteo': conteo.to_dict(orient='records'),
        'predicciones': resultados,
        'ultima_fecha': ultima_fecha.fecha_entrenamiento if ultima_fecha else None,
        'explicacion': (
            "El modelo Naive Bayes clasifica automaticamente los consumos del usuario "
            "en tres niveles (bajo, medio, alto) según los datos historicos. "
            "Ademas, guarda cada prediccion realizada en la base de datos para "
            "permitir el seguimiento y analisis del historial."
        )
    }

    return render(request, 'bayes.html', context)

def historial_bayes(request):#Vista del historial del modelo
    historial = ClasificacionBayes.objects.filter(usuario=request.user).order_by('-fecha_prediccion')
    return render(request, 'historial_bayes.html', {'historial': historial})




