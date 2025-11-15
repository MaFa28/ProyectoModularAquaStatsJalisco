# Obtiene los datos de la BDD si no existen arroja error
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages  # Enviar mensajes temporales al usuario
# importar el form de django
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User  # metodo para registro de usuarios
from django.contrib.auth import login, logout, authenticate  # Metodos de autenticacion
from django.contrib.auth.decorators import login_required  # Proteger las rutas
from django.db import IntegrityError  # Errores en DB
from django.http import HttpResponse, FileResponse  # mensajes en pantalla
from .formdom import RegistroDom, RegistroCosumo, RegistroForm  # Traer mis formularios
from .models import recomendaciones, consumoagua, domicilior, RegresionMetricas, ClasificacionBayes, EntrenamientoBayes, KMeansResultado  # Traer mis modelos
from django.core.paginator import Paginator  # Agregar paginacion en la tabla
import openpyxl  # Para trabajar con archivos de excel
import io  # Trabajar con los PDF
import re  # validacion del correo
import pandas as pd  # Manejo de datos
import numpy as np  # Manejo de datos y los muestra en graficas
import plotly.express as px  # Manejo de datos y muestra datos en dashboard
from datetime import datetime  # para convertir la informacion para exportar
from reportlab.lib.pagesizes import letter  # Crear PDF
from reportlab.lib import colors  # Crear PDF
from django.contrib.staticfiles import finders
from django.utils import timezone  # manejo de fechas y horas
from django.conf import settings # Crear PDF
from reportlab.lib.units import mm # Crear PDF
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle # Crear PDF
# Estilos en el PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
# Trae el algoritmo de Regresion lineal
from sklearn.linear_model import LinearRegression
# Auxiliares para los algoritmos
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.naive_bayes import GaussianNB  # Trae el algoritmo de Bayes
from sklearn.preprocessing import StandardScaler  # Auxiliar de los algoritmos
from sklearn.cluster import KMeans  # Trae el ALgoritmo de Kmeans
from django.db.models import Avg, Count, Max  # Herramientas auxiliares de Kmeans
from django.conf import settings  # Herramientas auxiliares de Kmeans
import os  # Herramientas auxiliares de Kmeans
# Trae el modelo de la ia
from .utils.ia_hibrida import entrenar_modelo, predecir_consumo
# trae el modelo del sistema experto
from .utils.sistema_experto import sistema_experto
import plotly.graph_objects as go  # apoyo en las graficas
# trae el modelo de guardar recomendaciones
from .utils.help import guardar_recomendacion


# Create your views here.


def home(request):  # Vista del Inicio
    # Ruta de las imagenes
    carpeta_carrusel = os.path.join(
        settings.BASE_DIR, 'consulta/static/img/carrusel')

    # Diccionario de nombres y descripciones
    descripciones = {
        'img1.png': {
            'titulo': 'AquaStats',
            'descripcion': 'Promovemos el consumo sostenible para un futuro mejor.'
        },
        'img2.png': {
            'titulo': 'Jalisco Dia 0',
            'descripcion': 'Jalisco esta en una situacion hidrica cambiante que lo mantiene de momento alejado del "DIA 0" debido a las lluvias del 2025.'
        },
        'img3.jpeg': {
            'titulo': 'Estrés hidráulico',
            'descripcion': 'Causas: "Acuíferos Sobreexplotados, Crecimiento poblacional y urbano, Uso agrícola intensivo, Impacto del cambio climático, Gestión y distribución"'
        },
        'img4.png': {
            'titulo': 'Nuestros Rios',
            'descripcion': 'Jalisco cuenta con una gran red hidraulica, entre los rios mas importantes se encuentra: "Rio Lerma-Santiago, Ameca, Verde, Bolaños, Costa"'
        },
        'img5.png': {
            'titulo': 'Nuestros Mantso Acuiferos',
            'descripcion': 'Jalisco cuenta con 76 mantos acuiferos los cuales se encargan de suministrar agua a zonas agricolas y a las principales ciudades, entre los que destacan "Toluqilla, Atemajac, La Barca, La Costa, Los Altos", los cuales ante el creciemiento de la poblacion se han visto afectados, por las actividades cotidianas, de riego y industriales'
        },
        'img6.png': {
            'titulo': 'Nuestros Lagos y Lagunas',
            'descripcion': 'El "Lago de Chapala" abastece el "60%" al Area Metropolitana lo cual causa un estres hidrico, el cual se ve reflejado año con año, ademas de del "Lago de Chapala" Jalisco cuenta con "Laguna de Cajititlán, Zapotlán, Sayula, Atotonilco, San Marcos, Zacoalco"'
        },
    }

    # Obtiene la lista de imagenes disponibles
    imagenes = []
    if os.path.exists(carpeta_carrusel):
        for archivo in os.listdir(carpeta_carrusel):
            if archivo.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                info = descripciones.get(
                    archivo, {'titulo': archivo, 'descripcion': 'Sin descripción'})
                imagenes.append({
                    'archivo': f'img/carrusel/{archivo}',
                    'titulo': info['titulo'],
                    'descripcion': info['descripcion']
                })

    # Ordenar las imágenes alfabéticamente (opcional)
    imagenes.sort(key=lambda x: x['archivo'])

    return render(request, 'inicio.html', {'imagenes': imagenes})


def sigup(request):  # Vista del Registro de Usuario
    if request.method == 'GET':  # Metodo GET: muestra el formulario
        return render(request, 'registro.html', {"form": None})
    else:
        # Captura de datos del formulario
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        # Validacion de contraseñas
        if password1 != password2:
            return render(request, 'registro.html', {
                "error": "Las contraseñas no coinciden."
            })

        # Validacion de formato de correo electronico
        patron_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(patron_email, email):
            return render(request, 'registro.html', {
                "error": "El correo electrónico no tiene un formato válido."
            })

        # Validacion de duplicado de correo
        if User.objects.filter(email__iexact=email).exists():
            return render(request, 'registro.html', {
                "error": "Este correo electrónico ya está registrado."
            })

        # Creación del usuario
        try:
            user = User.objects.create_user(
                username=username,
                password=password1,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            user.save()

            login(request, user)  # Inicia sesion automaticamente
            return redirect('domicilio')  # Redirige al inicio o perfil

        except IntegrityError:
            return render(request, 'registro.html', {
                "error": "Este nombre de usuario ya existe."
            })


def salir(request):  # Vista para cerrar sesion
    logout(request)
    return redirect('home')


def inicio(request):  # Vista inicio de sesion
    if request.method == 'GET':  # Renvio del formulario
        return render(request, 'insesion.html', {
            'form': AuthenticationForm
        })
    else:  # Metodo para revisar que el usuario exista
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:  # Revisar si la contraseña o usuario existen
            return render(request, 'insesion.html', {
                'form': AuthenticationForm,
                'error': 'Usuario o contraseña incorrecta'
            })
        else:
            login(request, user)  # Usuario existente
            return redirect('perfil')


@login_required  # Protege los endpoints si el usuario no esta logeado
def domicilio(request):  # Vista de registro de domicilio
    if request.method == 'GET':  # Si la peticion en GET regresa el formulario
        return render(request, 'domicilio.html', {
            'form': RegistroDom
        })
    else:
        try:  # logica para guardar los datos en la Base de Datos
            Form = RegistroDom(request.POST)
            if Form.is_valid():
                nuevo_dom = Form.save(commit=False)
                nuevo_dom.id_usuario = request.user  # Solicta el usuario a la base de datos
                nuevo_dom.save()  # Guarda la informacion en la base datos
                return redirect('ver_domicilios')
            else:
                return render(request, 'domicilio.html', {
                    'form': RegistroDom,
                    'error': 'Ingresa datos validos'
                })
        except Exception as e:  # Muestra error en pantalla si no se completan los datos
            return render(request, 'domicilio.html', {
                'form': RegistroDom,
                'error': f'Ocurrio un error'
            })


@login_required  # Protege los endpoints si el usuario no esta logeado
def ver_domicilios(request):  # Vista para ver los domicilios registrados
    # Filtrado de domicilios del usuario logeado
    domicilios = domicilior.objects.filter(id_usuario=request.user)
    return render(request, 'domicilios.html', {
        'domicilios': domicilios
    })


@login_required  # Protege los endpoints si el usuario no esta logeado
def editar_domicilio(request, domicilio_id):
    # Metodo para evitar que otros usuarios modifiquen formularios que no sean suyos
    domicilio = get_object_or_404(
        domicilior, id=domicilio_id, id_usuario=request.user)

    if request.method == 'POST':  # Metodo POST
        form = RegistroDom(request.POST, instance=domicilio)
        if form.is_valid():  # Revisa si la informacion es valida
            form.save()  # Guarda la informacion
            return redirect('ver_domicilios')  # redirecciona a la vista
    else:  # Si no se cumple la condicion regresa el form otra vez
        # Si no se cumple la condicion regresa el form otra vez
        form = RegistroDom(instance=domicilio)
    return render(request, 'editardomi.html', {
        'form': form
    })


@login_required  # Protege los endpoints si el usuario no esta logeado
def eliminar_domicilio(request, domicilio_id):

    # Si no se cumple la condicion regresa el form otra vez
    domicilio = get_object_or_404(
        domicilior, id=domicilio_id, id_usuario=request.user)

    if request.method == 'POST':  # Metodo POST
        domicilio.delete()  # Elimina el domicilio de la base de datos
        return redirect('ver_domicilios')  # Redirecciona a los domicilios

    return render(request, 'eliminardomi.html', {  # Regresa el mismo formulario a pantalla
        'domicilio': domicilio
    })


@login_required  # Protege los endpoints si el usuario no esta logeado
def perfil(request):  # Vista perfil

    # Filtros
    tipo = request.GET.get('tipo')
    fecha = request.GET.get('fecha')

    # Filtrado de reportes del usuario logeado
    reportes = consumoagua.objects.filter(id_usuario=request.user)

    if tipo:
        reportes = reportes.filter(tipo_reporte=tipo)
    if fecha:
        reportes = reportes.filter(fecha=fecha)

    reportes = reportes.order_by('-fecha')

    # Paginacion
    paginator = Paginator(reportes, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'perfil.html', {
        'page_obj': page_obj,  # Elementos que se mandan a la vista
        'tipo': tipo,
        'fecha': fecha,
    })


@login_required
def reporte(request):  # Vista para crear reportes
    if request.method == 'GET':
        form = RegistroCosumo()
        # Filtrar domicilios solo del usuario actual
        form.fields['id_domicilio'].queryset = domicilior.objects.filter(
            id_usuario=request.user)

        return render(request, 'reporte.html', {
            'form': form
        })

    else:
        try:
            form = RegistroCosumo(request.POST)
            # Repetimos el filtrado por seguridad 
            form.fields['id_domicilio'].queryset = domicilior.objects.filter(
                id_usuario=request.user)

            if form.is_valid():
                nuevo_rep = form.save(commit=False)
                nuevo_rep.id_usuario = request.user
                nuevo_rep.save()
                return redirect('perfil')

            else:
                return render(request, 'reporte.html', {
                    'form': form,
                    'error': 'Por favor ingresa datos válidos.'
                })

        except Exception as e:
            return render(request, 'reporte.html', {
                'form': form,
                'error': f'Ocurrió un error al guardar el reporte: {e}'
            })


@login_required
def editar_reporte(request, id):  # Vista para editar reportes
    # Evita que un usuario modifique un reporte que no es suyo
    reporte = get_object_or_404(consumoagua, id=id, id_usuario=request.user)

    # Procesa el formulario
    if request.method == 'POST':
        form = RegistroCosumo(request.POST, instance=reporte)
        # Filtra los domicilios que pertenezcan al usuario logeado
        form.fields['id_domicilio'].queryset = domicilior.objects.filter(
            id_usuario=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, ' Reporte actualizado correctamente.')
            return redirect('perfil')
        else:
            messages.error(request, ' Error al actualizar el reporte.')
    else:
        form = RegistroCosumo(instance=reporte)
        # Filtrado en el GET
        form.fields['id_domicilio'].queryset = domicilior.objects.filter(
            id_usuario=request.user)

        # Si el usuario no tiene domicilios registrados
        if not form.fields['id_domicilio'].queryset.exists():
            messages.warning(
                request, 'No tienes domicilios registrados. Debes agregar uno antes de editar reportes.')

    # Renderizado del formulario
    return render(request, 'editarrepo.html', {
        'form': form
    })


@login_required  # Protege los endpoints si el usuario no esta logeado
def eliminar_reporte(request, id):  # Vista para eliminar los reportes
    # Metodo para evitar que otros usuarios eliminen formularios que no sean suyos
    reporte = get_object_or_404(consumoagua, id=id, id_usuario=request.user)

    if request.method == 'POST':
        reporte.delete()  # Metodo para eliminar el reporte
        messages.success(request, 'Reporte eliminado')
        return redirect('perfil')
    return render(request, 'eliminarrepo.html', {
        'reporte': reporte
    })


@login_required  # Protege los endpoints si el usuario no esta logeado
def exportar_excel(request):  # Vista para exportar archivos a EXCEl
    # Filtros
    tipo = request.GET.get('tipo')
    fecha = request.GET.get('fecha')

    # Obtiene los datos del usuario logeado
    reportes = consumoagua.objects.filter(id_usuario=request.user)
    if tipo:
        reportes = reportes.filter(tipo_reporte=tipo)
    if fecha:
        try:  # Convertir la fecha antes de filtrar
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
            reportes = reportes.filter(fecha=fecha_obj)
        except:
            pass  # Ignora el formato

    # Crear el libro de excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reportes Consumo de Agua"

    # Agregar encabezado
    ws.append(["Cantidad M3", "Tipo reporte", "Fecha", "Domicilio"])

    # Insertar filas
    for r in reportes:
        ws.append([
            r.cantidad,
            r.get_tipo_reporte_display(),
            r.fecha.strftime("%d/%m/%Y"),
            r.id_domicilio.direccion,
        ])

    # Respuesta HTTP
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",)
    response["Content-Disposition"] = 'attachment; filename="reportes_consumo.xlsx"'
    wb.save(response)
    return response

@login_required# Protege los endpoints si el usuario no esta logeado
def exportar_pdf(request):# Vista para exportar archivos a PDF

    # Filtros 
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
            pass

    # Documento 
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=26*mm, rightMargin=18*mm,
        topMargin=36*mm, bottomMargin=20*mm
    )

    styles = getSampleStyleSheet()
    def add_style_safe(s):
        if s.name not in styles.byName:
            styles.add(s)
    add_style_safe(ParagraphStyle(name="AquaH2", fontName="Helvetica-Bold",
                                  fontSize=12, leading=14.5, textColor=colors.HexColor("#0B2347"),
                                  spaceBefore=10, spaceAfter=6))
    add_style_safe(ParagraphStyle(name="AquaMeta", fontName="Helvetica",
                                  fontSize=9.5, textColor=colors.HexColor("#6B7280"),
                                  spaceAfter=12))
    add_style_safe(ParagraphStyle(name="AquaCard", fontName="Helvetica-Bold",
                                  fontSize=12.5, textColor=colors.HexColor("#111827"), alignment=1))
    add_style_safe(ParagraphStyle(name="AquaCardSub", fontName="Helvetica",
                                  fontSize=9.8, textColor=colors.HexColor("#374151"), alignment=1))

    elements = []

    # Marca de agua
    LOGO_REL = 'img/carrusel/img1.png'
    logo_path = finders.find(LOGO_REL)
    if not logo_path:
        try:
            candidate = os.path.join(getattr(settings, 'STATIC_ROOT', ''), LOGO_REL)
            if candidate and os.path.exists(candidate):
                logo_path = candidate
        except Exception:
            pass
    if not logo_path:
        for base in getattr(settings, 'STATICFILES_DIRS', []):
            candidate = os.path.join(base, LOGO_REL)
            if os.path.exists(candidate):
                logo_path = candidate
                break

    # Encabezado / Pie / Marca de agua 
    def _header_footer(canvas, _doc):
        canvas.saveState()

        # Marca de agua centrada
        if logo_path:
            try:
                page_w, page_h = canvas._pagesize
                wm_w = 120*mm; wm_h = 120*mm
                x = (page_w - wm_w) / 2
                y = (page_h - wm_h) / 2
                try:
                    canvas.setFillAlpha(0.06); canvas.setStrokeAlpha(0.06)
                except Exception:
                    pass
                canvas.drawImage(logo_path, x, y, width=wm_w, height=wm_h,
                                 preserveAspectRatio=True, mask='auto')
                try:
                    canvas.setFillAlpha(1); canvas.setStrokeAlpha(1)
                except Exception:
                    pass
            except Exception:
                pass

        # Banda superior 
        band_h = 16*mm
        band_y = _doc.height + _doc.topMargin - band_h - 8*mm
        canvas.setFillColor(colors.HexColor("#1A7DFF"))
        canvas.roundRect(_doc.leftMargin-10*mm, band_y,
                         _doc.width + 20*mm, band_h, 7*mm, stroke=0, fill=1)

        # Logo pequeño en la banda 
        if logo_path:
            try:
                canvas.drawImage(
                    logo_path,
                    _doc.leftMargin - 2*mm,
                    band_y + (band_h - 12*mm)/2,
                    width=12*mm, height=12*mm, mask='auto'
                )
            except Exception:
                pass

        # Título en la banda 
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(
            _doc.leftMargin + 14*mm,
            band_y + band_h/2 - 4,
            "Reporte de Consumo de Agua"
        )

        # Pie de página
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.HexColor("#6B7280"))
        canvas.drawString(_doc.leftMargin, 13*mm,
                          f"Generado: {timezone.now().strftime('%d/%m/%Y %H:%M')}  •  Usuario: {request.user.username}")
        canvas.drawRightString(_doc.leftMargin + _doc.width, 13*mm, f"Página {_doc.page}")

        canvas.restoreState()

    # Meta 
    elements.append(Spacer(1, 8*mm))  #Espaciado
    elements.append(Paragraph(
        f"Filtros aplicados: Tipo = {tipo or 'Todos'} • Fecha = {fecha or '—'}",
        styles["AquaMeta"]
    ))

    # Resumen 
    total_registros = reportes.count()
    total_m3 = sum((r.cantidad for r in reportes), 0)
    avg_m3 = (float(total_m3) / total_registros) if total_registros else 0.0

    cards_data = [
        [Paragraph(f"{total_m3:.2f} m³", styles["AquaCard"]),
         Paragraph(f"{avg_m3:.2f} m³", styles["AquaCard"]),
         Paragraph(f"{total_registros}", styles["AquaCard"])],
        [Paragraph("Consumo total", styles["AquaCardSub"]),
         Paragraph("Promedio por reporte", styles["AquaCardSub"]),
         Paragraph("Reportes generados", styles["AquaCardSub"])],
    ]
    cards = Table(cards_data, colWidths=[50*mm, 50*mm, 50*mm], rowHeights=[14*mm, 10*mm])
    cards.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.9, colors.HexColor("#E5E7EB")),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#E5E7EB")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements += [cards, Spacer(1, 18)]

    elements += [Paragraph("Detalle de registros", styles["AquaH2"]), Spacer(1, 8)]

    #  Tabla 
    data = [["Usuario", "Consumo (m³)", "Tipo", "Domicilio", "Fecha"]]
    for r in reportes:
        data.append([
            r.id_usuario.username,
            f"{r.cantidad}",
            r.get_tipo_reporte_display(),
            r.id_domicilio.direccion,
            r.fecha.strftime("%d/%m/%Y"),
        ])
    if len(data) == 1:
        data.append(["—", "—", "—", "No se encontraron registros con los filtros.", "—"])

    table = Table(data, colWidths=[40*mm, 28*mm, 28*mm, 64*mm, 28*mm], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A7DFF")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10.5),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9.8),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor("#111827")),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('ALIGN', (4, 1), (4, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FAFBFF"), colors.white]),
        ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),

        ('LEFTPADDING', (0, 1), (-1, -1), 8),
        ('RIGHTPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 7),
    ]))
    elements.append(table)

    #  Render 
    doc.build(elements, onFirstPage=_header_footer, onLaterPages=_header_footer)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="reportes_consumo.pdf")

@login_required  # Protege los endpoints si el usuario no esta logeado
# Vista para vizualizar todos los reportes de manera global
def reportes_publicos(request):
    # Llamado a la BDD
    reportes = consumoagua.objects.select_related('id_usuario', 'id_domicilio')

    #Filtros
    tipo_reporte = request.GET.get('tipo_reporte')
    region = request.GET.get('region')
    usuario = request.GET.get('usuario')
    tipo_consumo = request.GET.get('tipo_consumo')

    if tipo_reporte:
        reportes = reportes.filter(tipo_reporte=tipo_reporte)

    if region:
        reportes = reportes.filter(id_domicilio__region=region)

    if usuario:
        reportes = reportes.filter(id_usuario__username__icontains=usuario)

    if tipo_consumo:
        reportes = reportes.filter(tipo_consumo=tipo_consumo)

    # Paginación 
    paginator = Paginator(reportes, 10)  # 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Exportar 
    exportar_excel = 'exportar_excel' in request.GET
    exportar_todo = request.GET.get('exportar_todo', '0') == '1'

    if exportar_excel:
        # Si exporta todo, usamos el queryset filtrado completo
        # Si no, solo los registros de la página actual
        if exportar_todo:
            qs_export = reportes
        else:
            qs_export = page_obj.object_list

        data = [
            {
                'Usuario': r.id_usuario.username,
                'Consumo (m3)': r.cantidad,
                'Región': r.id_domicilio.region,
                'Tipo de Reporte': r.get_tipo_reporte_display(),
                'Tipo de Consumo': r.get_tipo_consumo_display() if r.tipo_consumo else '',
            }
            for r in qs_export
        ]

        df = pd.DataFrame(data)
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        nombre = "reportes_todos.xlsx" if exportar_todo else "reportes_pagina.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{nombre}"'
        df.to_excel(response, index=False)
        return response

    # Render de la vista 
    return render(request, 'reportes_publicos.html', {
        'page_obj': page_obj,
        'reportes': page_obj.object_list,  # lo que usa la tabla
        'tipo_reporte': tipo_reporte,
        'region': region,
        'usuario': usuario,
        'tipo_consumo': tipo_consumo,
    })

@login_required  # Protege los endpoints si el usuario no esta logeado
# Vista para ver un remusen del consumo, en forma de tabla y grafica, ademas muestra anomalias
def analisis_usuario(request):
    reportes = consumoagua.objects.filter(id_usuario=request.user).select_related(
        'id_domicilio')  # Obtiene solo los reportes de el usuario logeado

    if not reportes.exists():  # Verifica que existan reportes
        return render(request, 'analisis_usuario.html', {'mensaje': 'No hay registros de consumo disponibles.'})
    # Covertir los datos a un dataframe
    data = []
    for r in reportes:
        data.append({
            'fecha': r.fecha or timezone.now().date(),
            'cantidad': float(r.cantidad or 0),
            'region': getattr(r.id_domicilio, 'region', '—'),
            'domicilio': getattr(r.id_domicilio, 'direccion', '—'),
        })
    # Formatp para las fechas
    df = pd.DataFrame(data)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['mes'] = df['fecha'].dt.to_period('M')
    # Calculo de metricas
    promedio = df['cantidad'].mean()
    desviacion = df['cantidad'].std()
    maximo = df['cantidad'].max()
    minimo = df['cantidad'].min()

    # Detectar consumos anormales
    df['anormal'] = np.where(
        (df['cantidad'] > promedio + 2 *
         desviacion) | (df['cantidad'] < promedio - 2*desviacion),
        True, False
    )

    # Agrupar por mes
    tendencia = df.groupby('mes')['cantidad'].mean().reset_index()

    # Generar alertas
    alertas = []
    if len(tendencia) > 1:
        tendencia = tendencia.sort_values(by='mes')
        for i in range(1, len(tendencia)):
            mes_actual = tendencia.iloc[i]
            mes_anterior = tendencia.iloc[i - 1]
            if mes_anterior['cantidad'] != 0:
                cambio = (
                    (mes_actual['cantidad'] - mes_anterior['cantidad']) / mes_anterior['cantidad']) * 100
                if cambio > 30:
                    alertas.append(
                        {'tipo': 'aumento', 'mensaje': f" Tu consumo aumentó un {cambio:.1f}% en {mes_actual['mes']} respecto al mes anterior."})
                elif cambio < -30:
                    alertas.append(
                        {'tipo': 'disminucion', 'mensaje': f" Tu consumo disminuyó un {abs(cambio):.1f}% en {mes_actual['mes']} respecto al mes anterior."})

    # Una vez obtenida la informacion esta se agrupa y se envia a la vista
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


@login_required  # Protege los endpoints si el usuario no esta logeado
# Vista para ver datos de manera global de todos los usuarios
def dashboard_global(request):
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
    graf1 = px.line(df, x='Fecha', y='Cantidad', color='Usuario',
                    title='Tendencia de Consumo por Usuario')

    graf2 = px.bar(
        df.groupby(['Usuario', 'Tipo de Reporte'])[
            'Cantidad'].mean().reset_index(),
        x='Usuario', y='Cantidad', color='Tipo de Reporte',
        title='Promedio por Usuario y Tipo de Reporte'
    )

    graf3 = px.pie(df, names='Region', title='Distribución por Región')

    graf4 = px.box(df, x='Usuario', y='Cantidad',
                   title='Distribución del Consumo por Usuario')

    #funciones definidas:
    modelo, mse, r2 = entrenar_modelo(df)
    mes_actual_dt = df['Fecha'].max()
    mes_siguiente = df['Fecha'].dt.month.max() + 1
    prediccion_futura = predecir_consumo(mes_siguiente, modelo)

    consumo_promedio = df['Cantidad'].mean()
    categoria_bayes = "IA"   # placeholder
    cluster = 2              # placeholder

    # Sistema experto + IA
    recomendacion = sistema_experto(
        consumo_promedio, prediccion_futura, categoria_bayes, cluster)
    # `recomendacion` es una lista de textos

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # GUARDADO SEGURO DE RECOMENDACIONES
    # Unimos los puntos y guardamos UNA sola recomendación del día
    if request.user.is_authenticated and recomendacion:
        texto_general = " • ".join(recomendacion)
        guardar_recomendacion(request.user, texto_general, algoritmo='general')
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Serie mensual histórica promedio por mes
    df_mensual = (
        df.groupby(df['Fecha'].dt.to_period('M'))['Cantidad']
          .mean()
          .reset_index()
    )
    df_mensual['Periodo'] = df_mensual['Fecha'].dt.to_timestamp()
    df_mensual.rename(columns={'Cantidad': 'PromedioMensual'}, inplace=True)

    # Punto futuro para mostrar la predicción
    next_period_ts = (mes_actual_dt.to_period('M') + 1).to_timestamp()

    fig_cmp = go.Figure()
    # Línea histórica
    fig_cmp.add_trace(go.Scatter(
        x=df_mensual['Periodo'], y=df_mensual['PromedioMensual'],
        mode='lines+markers', name='Histórico (promedio mensual)'
    ))
    # Proyección
    if not df_mensual.empty and prediccion_futura is not None:
        fig_cmp.add_trace(go.Scatter(
            x=[df_mensual['Periodo'].iloc[-1], next_period_ts],
            y=[df_mensual['PromedioMensual'].iloc[-1], prediccion_futura],
            mode='lines', name='Proyección', line=dict(dash='dash')
        ))
        fig_cmp.add_trace(go.Scatter(
            x=[next_period_ts], y=[prediccion_futura],
            mode='markers', name='Predicción IA',
            marker=dict(size=11, symbol='diamond')
        ))

    fig_cmp.update_layout(
        title='Consumo Histórico vs Predicción IA',
        xaxis_title='Mes',
        yaxis_title='Consumo (m³)',
        legend_title='Serie'
    )

    # --- Contexto para el template ---
    context = {
        'graf1': graf1.to_json(),
        'graf2': graf2.to_json(),
        'graf3': graf3.to_json(),
        'graf4': graf4.to_json(),
        'graf5': fig_cmp.to_json(),
        'recomendaciones': recomendacion,
        'mse': round(mse, 2) if mse is not None else None,
        'r2': round(r2, 3) if r2 is not None else None,
        'prediccion': round(prediccion_futura, 2) if prediccion_futura is not None else None,
    }

    return render(request, 'dashboard.html', context)


# Vista que procesa los datos para guardar en la base de datos
def procesar_regresion(reportes, usuario=None):
    # Recibe y procesa los datos antes de guardar en la base datos
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
    df_mes = df.groupby('mes_num', as_index=False)[
        'cantidad'].mean().sort_values('mes_num')
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
    # Retorna los elementos listos
    return {
        'r2': round(r2, 3),
        'mse': round(mse, 2),
        'b0': round(b0, 3),
        'b1': round(b1, 3),
        'prediccion': round(prediccion, 2),
        'datos': df_mes.to_dict(orient='records')
    }


@login_required  # Protege los endpoints si el usuario no esta logeado
# Vista que aplica el algoritmo de regresion lineal a un solo usuario
def regresion_lineal(request):
    # Obtiene los datos desde la base de datos
    reportes = consumoagua.objects.filter(
        id_usuario=request.user).select_related('id_domicilio')
    df = pd.DataFrame(list(reportes.values('fecha', 'cantidad')))

    if df.empty:
        return render(request, 'regresion.html', {'empty': True})

    # Limpia los datos
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce')
    df = df.dropna(subset=['fecha', 'cantidad'])
    df = df[df['cantidad'] > 0]

    if df.empty:
        return render(request, 'regresion.html', {'empty': True})

    # Agrupa por mes
    df['mes_num'] = df['fecha'].dt.month
    df_mes = df.groupby('mes_num', as_index=False)['cantidad'].mean()

    if len(df_mes) < 2:
        return render(request, 'regresion.html', {
            'empty': True,
            'mensaje': 'Se necesitan al menos 2 meses de datos para la regresión.'
        })

    # Prepara las variables para el modelo
    X = df_mes[['mes_num']]
    y = df_mes['cantidad']

    # Entrena el modelo
    modelo = LinearRegression()
    modelo.fit(X, y)

    # Calcula predicciones y métricas
    y_pred = modelo.predict(X)
    r2 = r2_score(y, y_pred)
    mse = mean_squared_error(y, y_pred)

    # Coeficientes del modelo
    b0 = modelo.intercept_      # Intercepto (β₀)
    b1 = modelo.coef_[0]        # Pendiente (β₁)

    # Predicción para el siguiente mes
    mes_siguiente = X['mes_num'].max() + 1
    prediccion_futura = modelo.predict([[mes_siguiente]])[0]

    usuario_data = procesar_regresion(reportes, request.user)

    # Recomendaciones automáticas
    promedio_actual = y.mean()
    if prediccion_futura > promedio_actual * 1.15:
        texto = (
            f"Tu consumo proyectado para el próximo mes ({prediccion_futura:.2f} m³) "
            f"supera en más del 15% tu promedio actual ({promedio_actual:.2f} m³). "
            "Revisa posibles fugas o reduce el uso en horarios de alta demanda."
        )
    elif prediccion_futura < promedio_actual * 0.85:
        texto = (
            f"Se proyecta una reducción en tu consumo ({prediccion_futura:.2f} m³). "
            "¡Excelente! Continúa con tus hábitos de ahorro de agua."
        )
    else:
        texto = (
            f"Tu consumo proyectado ({prediccion_futura:.2f} m³) se mantiene estable "
            "en relación con tu promedio. No se detectan cambios significativos."
        )

    # Metodo para guardar las recomendaciones
    from .utils.help import guardar_recomendacion
    guardar_recomendacion(request.user, texto, algoritmo='regresion')

    # Prepara los datos para la vista
    context = {
        'r2': round(r2, 3),
        'mse': round(mse, 2),
        'prediccion': round(prediccion_futura, 2),
        'b0': round(b0, 3),
        'b1': round(b1, 3),
        'datos': df_mes.to_dict(orient='records'),
        'usuario': usuario_data,
        'recomendacion': texto,
        'explicacion': (
            "Se aplicó un modelo de regresión lineal simple para estimar la tendencia del consumo "
            "mensual de agua. El modelo ajusta una línea recta a los valores promedio por mes, "
            "evaluando su precisión mediante el coeficiente de determinación (R²) y el error cuadrático medio (MSE). "
            "Finalmente, se realizó una predicción para el siguiente mes basada en la tendencia calculada."
        )
    }

    return render(request, 'regresion.html', context)


@login_required  # Protege los endpoints si el usuario no esta logeado
# Vista que aplica el algoritmo de regresion lineal para todos los usuarios
def regresion_global(request):
    # Obtiene los datos desde la base de datos
    reportes = consumoagua.objects.all()
    df = pd.DataFrame(list(reportes.values('fecha', 'cantidad')))

    if df.empty:
        return render(request, 'regresion_global.html', {'empty': True})

    # Realiza Limpieza de datos
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

    # Entrenamiento del modelo
    modelo = LinearRegression()
    modelo.fit(X, y)

    # Calcula predicciones y metricas
    y_pred = modelo.predict(X)
    r2 = r2_score(y, y_pred)
    mse = mean_squared_error(y, y_pred)

    # Obtiene coeficientes del modelo
    b0 = modelo.intercept_      # Intercepto (β₀)
    b1 = modelo.coef_[0]        # Pendiente (β₁)

    # Calcula las predicciones para el siguiente mes
    mes_siguiente = X['mes_num'].max() + 1
    prediccion_futura = modelo.predict([[mes_siguiente]])[0]

    global_data = procesar_regresion(reportes, None)

    # Prepara los datos para la vista
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

    # Lo envia a el template
    return render(request, 'regresion_global.html', context)


@login_required  # Protege los endpoints si el usuario no esta logeado
def historial_metricas(request):  # Vista para ver las metricas
    metricas = RegresionMetricas.objects.filter(
        usuario=request.user).order_by('-fecha_entrenamiento')
    return render(request, 'historial_metricas.html', {'metricas': metricas})


@login_required  # Protege los endpoints si el usuario no esta logeado
def reentrenar_bayes(request):  # Vista para que el usuario reentrene al modelo
    # Permite reentrenar manualmente el modelo Naive Bayes
    if request.method == 'POST':
        usuario = request.user

        # Obteniene los datos del usuario
        reportes = consumoagua.objects.select_related(
            'id_usuario').filter(id_usuario=usuario)
        df = pd.DataFrame(list(reportes.values('cantidad')))

        if df.empty:
            messages.warning(
                request, 'No hay datos suficientes para reentrenar el modelo.')
            return redirect('bayes')

        # Entrenamiento del modelo
        df['categoria'] = pd.qcut(df['cantidad'], q=3, labels=[
                                  'Bajo', 'Medio', 'Alto'])
        X = df[['cantidad']].values
        y = df['categoria'].values

        modelo = GaussianNB()
        modelo.fit(X, y)

        # Guardar la nueva fecha de entrenamiento
        EntrenamientoBayes.objects.create(
            usuario=usuario, fecha_entrenamiento=datetime.now())

        # Guarda las clasificaciones actualizadas
        ClasificacionBayes.objects.filter(usuario=usuario).delete()
        for valor, clase in zip(X.flatten(), y):
            ClasificacionBayes.objects.create(
                usuario=usuario, consumo=valor, categoria=clase)
        # Mensaje si el modelo se actualizo correctamente
        messages.success(
            request, 'El modelo Bayesiano fue reentrenado correctamente.')
        return redirect('bayes')


@login_required  # Protege los endpoints si el usuario no esta logeado
# Vista con la logica necesaria para ejecutar el modelo de Bayes
def clasificacion_bayes(request):
    usuario = request.user  # revisa credendicales del usuario
    reportes = consumoagua.objects.select_related(
        'id_domicilio', 'id_usuario').filter(id_usuario=usuario)

    df = pd.DataFrame(list(reportes.values(
        'cantidad', 'id_usuario__username', 'id_domicilio__region')))
    if df.empty:
        return render(request, 'bayes.html', {'empty': True})

    # Prepara los datos
    df['categoria'] = pd.qcut(df['cantidad'], q=3, labels=[
                              'Bajo', 'Medio', 'Alto'])
    X = df[['cantidad']].values
    y = df['categoria'].values

    # Realiza una escala de  valores
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Entrenamiento del  modelo
    modelo = GaussianNB()
    modelo.fit(X_scaled, y)

    # Prediccion para los nuevos valores
    nuevos = np.array([[10], [50], [100], [500], [1000]])
    nuevos_scaled = scaler.transform(nuevos)
    predicciones = modelo.predict(nuevos_scaled)

    resultados = list(zip(nuevos.flatten(), predicciones))

    # Guarda las predicciones en la base de datos
    for valor, categoria in resultados:
        ClasificacionBayes.objects.create(
            usuario=usuario,
            consumo=valor,
            categoria=categoria
        )

    # Obtiene la categoria predominante del usuario
    categoria_usuario = df['categoria'].mode()[0]

    # Genera recomendaciones
    if categoria_usuario == 'Bajo':
        texto = (
            f"Tu consumo promedio es bajo. ¡Excelente trabajo! "
            "Continua con tus habitos sostenibles para conservar el agua."
        )
    elif categoria_usuario == 'Medio':
        texto = (
            f"Tu consumo esta en el rango medio. Considera revisar fugas y optimizar tu consumo "
            "en actividades diarias para reducirlo gradualmente."
        )
    else:
        texto = (
            f"Tu consumo se encuentra en el rango alto. Te recomendamos revisar tus instalaciones "
            "y adoptar practicas de ahorro para disminuir el gasto de agua."
        )
        # Metodo para guardar las recomendaciones
        from .utils.help import guardar_recomendacion
        guardar_recomendacion(request.user, texto, algoritmo='bayes')

    # Realiza un Conteo distribuciones
    conteo = df['categoria'].value_counts().reset_index()
    conteo.columns = ['Nivel', 'Cantidad']
    # Se aplica el reentrenamiento
    ultima_fecha = EntrenamientoBayes.objects.filter(
        usuario=usuario).order_by('-fecha_entrenamiento').first()

    # Envia los datos al template
    context = {
        'conteo': conteo.to_dict(orient='records'),
        'predicciones': resultados,
        'ultima_fecha': ultima_fecha.fecha_entrenamiento if ultima_fecha else None,
        'recomendacion': texto,
        'explicacion': (
            "El modelo Naive Bayes clasifica automaticamente los consumos del usuario "
            "en tres niveles (bajo, medio, alto) según los datos historicos. "
            "Ademas, guarda cada prediccion realizada en la base de datos para "
            "permitir el seguimiento y analisis del historial."
        )
    }

    return render(request, 'bayes.html', context)


@login_required  # Protege los endpoints si el usuario no esta logeado
def historial_bayes(request):  # Vista del historial del modelo
    historial = ClasificacionBayes.objects.filter(
        usuario=request.user).order_by('-fecha_prediccion')
    return render(request, 'historial_bayes.html', {'historial': historial})


@login_required  # Protege los endpoints si el usuario no esta logeado
def kmeans_view(request):  # Vista con la logica necesaria para ejecutar el modelo K-Means
    # Numero de clusteres
    k = int(request.GET.get('k', 3))

    # Obtiene los datos de la base de datos
    reportes = consumoagua.objects.select_related('id_usuario', 'id_domicilio')
    df = pd.DataFrame(list(reportes.values(
        'id_usuario__username', 'cantidad', 'id_domicilio__region'
    )))

    if df.empty:
        return render(request, 'kmeans.html', {'empty': True})

    # Renombra las columnas
    df = df.rename(columns={
        'id_usuario__username': 'Usuario',
        'id_domicilio__region': 'Región',
        'cantidad': 'Consumo'
    })

    df = df.dropna(subset=['Consumo'])
    df = df[df['Consumo'] > 0]
    # Si no existe informacion
    if df.empty:
        return render(request, 'kmeans.html', {'empty': True})

    # Aplica K-Means
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    df['Cluster'] = kmeans.fit_predict(df[['Consumo']])

    # Guardar los resultados en la base de datos
    # --- Buscar el consumo del usuario logeado ---
    usuario_actual = request.user.username
    df_usuario = df[df['Usuario'] == usuario_actual]

    recomendacion_usuario = None  # solo para el usuario actual

    for _, row in df.iterrows():
        try:
            usuario = User.objects.get(username=row['Usuario'])

            # Guardar resultados de K-Means
            KMeansResultado.objects.update_or_create(
                usuario=usuario,
                defaults={
                    'cluster': int(row['Cluster']),
                    'promedio_consumo': float(row['Consumo'])
                }
            )

            # Generar texto de recomendacion
            cluster = int(row['Cluster'])
            consumo = float(row['Consumo'])

            if cluster == 0:
                texto = (
                    f"Tu consumo actual ({consumo:.2f} m³) esta entre los mas bajos. "
                    "Excelente trabajo, sigue cuidando el agua."
                )
            elif cluster == 1:
                texto = (
                    f"Tu consumo ({consumo:.2f} m³) es promedio. "
                    "Podrias reducirlo ajustando habitos diarios o revisando fugas menores."
                )
            else:
                texto = (
                    f"Tu consumo ({consumo:.2f} m³) esta entre los mas altos. "
                    "Te recomendamos revisar fugas y considerar medidas de ahorro."
                )

            # Metodo para guardar las recomendaciones
            from .utils.help import guardar_recomendacion
            guardar_recomendacion(request.user, texto, algoritmo='kmeans')

            # Si es el usuario logeado, mostrarla
            if usuario.username == usuario_actual:
                recomendacion_usuario = texto

        except User.DoesNotExist:
            continue

    # Crea la tabla resumen
    resumen = (
        df.groupby('Cluster')
        .agg({'Consumo': ['mean', 'min', 'max', 'count']})
        .reset_index()
    )
    resumen.columns = ['Cluster', 'Promedio', 'Mínimo', 'Máximo', 'Cantidad']

    # Grafica
    grafica = px.scatter(
        df,
        x='Usuario', y='Consumo',
        color=df['Cluster'].astype(str),
        hover_data=['Región'],
        title=f'Agrupamiento K-Means del Consumo de Agua (k = {k})'
    )

    # Agrupa la informacion para enviarla a la vista
    context = {
        'grafica': grafica.to_json(),
        'tabla': resumen.to_dict(orient='records'),
        'k': k,
        'recomendacion_usuario': recomendacion_usuario,
    }

    return render(request, 'kmeans.html', context)


@login_required  # Protege los endpoints si el usuario no esta logeado
def historial_kmeans(request):  # Vista del historial del modelo K-Means

    # Obtiene los datos de la Base de Datos
    resultados = KMeansResultado.objects.select_related(
        'usuario').order_by('-fecha_analisis')

    if not resultados.exists():
        return render(request, 'historial_kmeans.html', {'empty': True})

    # Agrupa los datos por usuario para ver evolucion
    resumen = (
        KMeansResultado.objects.values('usuario__username')
        .annotate(
            total_analisis=Count('id'),
            ultimo_cluster=Max('cluster'),
            promedio_consumo=Avg('promedio_consumo')
        )
        .order_by('usuario__username')
    )

    # Crear DataFrame para graficar la evolucion temporal
    df = pd.DataFrame(list(resultados.values(
        'usuario__username', 'cluster', 'promedio_consumo', 'fecha_analisis'
    )))

    df['fecha_analisis'] = pd.to_datetime(df['fecha_analisis'])

    # Grafica de la evolucion del consumo
    grafica = px.line(
        df,
        x='fecha_analisis',
        y='promedio_consumo',
        color='usuario__username',
        markers=True,
        title='Evolución del Consumo Promedio por Usuario'
    )
    # Agrupa la informacion y la envia a la vista
    context = {
        'resumen': resumen,
        'resultados': resultados,
        'grafica': grafica.to_json(),
    }

    return render(request, 'historial_kmeans.html', context)

    hoy = timezone.now().date()
    obj, _ = recomendaciones.objects.update_or_create(
        id_usuario=user,
        algoritmo=algoritmo,
        fecha=hoy,
        defaults={'texto': texto},
    )
    return obj
