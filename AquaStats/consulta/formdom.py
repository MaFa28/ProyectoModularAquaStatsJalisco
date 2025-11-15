from django.forms import ModelForm #Para la creacion del formulario
from .models import domicilior, consumoagua
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

#Aqui se crean todos los formularios
class RegistroForm(UserCreationForm):#Se modifica el modelo usuario para usar su campo email
    email = forms.EmailField(
        label="Correo electrónico",
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "example@correo.com",
            "autocomplete": "email",
        }),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2") 

    # Evitar correos duplicados
    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class RegistroDom(ModelForm):#Modelo formulario registro domicilio
    class Meta:
        model = domicilior
        fields = ['direccion', 'colonia', 'municipio', 'region', 'miembros_domicilio']
        widgets = {
            #Elemento para agregar estilos a los inputs
            'direccion' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Ingresa tu direccion'}),
            'colonia' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Ingresa tu colonia'}),
            'municipio' : forms.Select(attrs={'class':'form-select'}),
            'region' : forms.Select(attrs={'class':'form-select'}),
            'miembros_domicilio': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de personas en el domicilio',
                'min': 1,
            }),
        }
        
class RegistroCosumo(forms.ModelForm):#Modelo del formulario registro de consumo de agua
    class Meta:
        model = consumoagua
        fields = ['cantidad', 'tipo_reporte', 'fecha', 'id_domicilio', 'tipo_consumo']
        widgets = {
            #Elemento para agregar estilos a los inputs
            'cantidad' : forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 90000}),
            'tipo_reporte' : forms.Select(attrs={'class':'form-select'}),
            'fecha' : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'id_domicilio' : forms.Select(attrs={'class': 'form-select'}),
            'tipo_consumo': forms.Select(attrs={'class': 'form-select'}),
        }