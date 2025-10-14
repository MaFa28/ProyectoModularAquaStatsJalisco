from django.forms import ModelForm #Para la creacion del formulario
from .models import domicilior, consumoagua
from django import forms

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
        
class RegistroCosumo(forms.ModelForm):#Modelo del formulario registro de consumo de agua
    class Meta:
        model = consumoagua
        fields = ['cantidad', 'tipo_reporte', 'fecha', 'id_domicilio']
        widgets = {
            #Elemento para agregar estilos a los inputs
            'cantidad' : forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 90000}),
            'tipo_reporte' : forms.Select(attrs={'class':'form-select'}),
            'fecha' : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'id_domicilio' : forms.Select(attrs={'class': 'form-select'})
        }