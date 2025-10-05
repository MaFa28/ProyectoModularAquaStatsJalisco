from django.forms import ModelForm #Para la creacion del formulario
from .models import domicilior, consumoagua
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
#Aqui se crean todos los formularios
class RegistroDom(ModelForm):#Modelo formulario registro domicilio
    class Meta:
        model = domicilior
        fields = ['direccion', 'colonia', 'municipio', 'region']
        widgets = {
            #Elemento para agregar estilos a los inputs
            'direccion' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Ingresa tu direccion'}),
            'colonia' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Ingresa tu colonia'}),
            'municipio' : forms.Select(attrs={'class':'form-select'}),
            'region' : forms.Select(attrs={'class':'form-select'})
        }
        
class RegistroCosumo(ModelForm):#Modelo del formulario registro de consumo de agua
    class Meta:
        model = consumoagua
        fields = ['cantidad', 'tipo_reporte', 'fecha']
        widgets = {
            #Elemento para agregar estilos a los inputs
            'cantidad' : forms.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(90000)]),
            'tipo_reporte' : forms.Select(attrs={'class':'form-select'}),
            'fecha' : forms.DateField()
        }