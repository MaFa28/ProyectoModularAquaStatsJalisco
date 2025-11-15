from django.db import models
from django.contrib.auth.models import User#importando la tabla usuario para la relacion
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from django.utils import timezone

# Create your models here.
class domicilior(models.Model): #Tabla domicilio
    REGION = {
        "RN" :  "Region Norte",
        "RAN" : "Region Altos Norte",
        "RAS" : "Region Altos Sur",
        "RC" :  "Region Cienega",
        "RSE" : "Region Sureste",
        "RS" : "Region Sur",
        "RSA" : "Region Sierra de Amula",
        "RCS" : "Region Costa Sur",
        "RCN" : "Region Costa Norte",
        "RSO" : "Region Sierra Occidental",
        "RV" : "Region Valles",
        "RCC" : "Region Centro",
    }
    MUNICIPIO = {
        "ACA" : "Acatic",
        "ACJ" : "Acatlán de Juárez",
        "ADM" : "Ahualulco de Mercado",
        "AMA" : "Amacueca",
        "AMT" : "Amatitán",
        "AM" : "Ameca",
        "AR" : "Arandas",
        "ATM" : "Atemajac de Brizuela",
        "AT" : "Atengo",
        "ATE" : "Atenguillo",
        "ATO" : "Atotonilco el Alto",
        "ATY" : "Atoyac",
        "AUN" : "Autlán de Navarro",
        "AYT" : "Ayotlán",
        "AYL" : "Ayutla",
        "BO" : "Bolaños",
        "CC" : "Cabo Corrientes",
        "CO" : "Cañadas de Obregón",
        "CCA" : "Casimiro Castillo",
        "CH" : "Chapala",
        "CHI" : "Chimaltitán",
        "CHQ" : "Chiquilistlán",
        "CIH" : "Cihuatlán",
        "CO" : "Cocula",
        "COL" : "Colotlán",
        "CBA" : "Concepción de Buenos Aires",
        "CGB" : "Cuautitlán de García Barragán",
        "CU" : "Cuautla",
        "CUQ" : "Cuquío",
        "DE" : "Degollado",
        "EH" : "Ejutla",
        "EA" : "El Arenal",
        "EG" : "El Grullo",
        "EL" : "El Limón",
        "ES" : "El Salto",
        "ED" : "Encarnación de Díaz",
        "ET" : "Etzatlán",
        "GF" : "Gómez Farías",
        "GU" : "Guachinango",
        "GUA" : "Guadalajara",
        "HOT" : "Hostotipaquillo",
        "HJ" : "Huejúcar",
        "HA" : "Huejuquilla el Alto",
        "IM" : "Ixtlahuacán de los Membrillos",
        "IR" : "Ixtlahuacán del Río",
        "JAL" : "Jalostotitlán",
        "JAM" : "Jamay",
        "JM" : "Jesús María",
        "JD" : "Jilotlán de los Dolores",
        "JTC" : "Jocotepec",
        "JU" : "Juanacatlán",
        "JUC" : "Juchitlán",
        "LB" : "La Barca",
        "LH" : "La Huerta",
        "LMP" : "La Manzanilla de la Paz",
        "LM" : "Lagos de Moreno",
        "MAG" : "Magdalena",
        "MAS" : "Mascota",
        "MAZ" : "Mazamitla",
        "MEX" : "Mexticacán",
        "MEZ" : "Mezquitic",
        "MIX" : "Mixtlán",
        "OCO" : "Ocotlán",
        "OJ" : "Ojuelos de Jalisco",
        "PI" : "Pihuamo",
        "PON" : "Poncitlán",
        "PTV" : "Puerto Vallarta",
        "QUI" : "Quitupan",
        "SCB" : "San Cristóbal de la Barranca",
        "SDA" : "San Diego de Alejandría",
        "SG" : "San Gabriel",
        "SICG" : "San Ignacio Cerro Gordo",
        "SJL" : "San Juan de los Lagos",
        "SJE" : "San Juanito de Escobedo",
        "SJ" : "San Julián",
        "SM" : "San Marcos",
        "SMB" : "San Martín de Bolaños",
        "SMH" : "San Martín Hidalgo",
        "SMA" : "San Miguel el Alto",
        "SPT" : "San Pedro Tlaquepaque",
        "SBO" : "San Sebastián del Oeste",
        "SMAA" : "Santa María de los Angeles",
        "SMO" : "Santa María del Oro",
        "SAY" : "Sayula",
        "TAL" : "Tala",
        "TLA" : "Talpa de Allende",
        "TG" : "Tamazula de Gordiano",
        "TAP" : "Tapalpa",
        "TEC" : "Tecalitlán",
        "TM" : "Techaluta de Montenegro",
        "TEO" : "Tecolotlán",
        "TEN" : "Tenamaxtlán",
        "TOA" : "Teocaltiche",
        "TOC" : "Teocuitatlán de Corona",
        "TEM" : "Tepatitlán de Morelos",
        "TQ" : "Tequila",
        "TCH" : "Teuchitlán",
        "TIA" : "Tizapán el Alto",
        "TLZ" : "Tlajomulco de Zuñiga",
        "TOLI" : "Tolimán",
        "TMT" : "Tomatlán",
        "TONA" : "Tonalá",
        "TONY" : "Tonaya",
        "TONI" : "Tonila",
        "TOTA" : "Totatiche",
        "TOTO" : "Tototlán",
        "TUX" : "Tuxcacuesco",
        "TUXC" : "Tuxcueca",
        "TUXP" : "Tuxpan",
        "USAA" : "Unión de San Antonio",
        "UT" : "Unión de Tula",
        "VG" : "Valle de Guadalupe",
        "VJ" : "Valle de Juárez",
        "VC" : "Villa Corona",
        "VIG" : "Villa Guerrero",
        "VH" : "Villa Hidalgo",
        "CP" : "Villa Purificación",
        "YA" : "Yahualica de González Gallo",
        "ZAT" : "Zacoalco de Torres",
        "ZAP" : "Zapopan",
        "ZAT" : "Zapotiltic",
        "ZAV" : "Zapotitlán de Vadillo",
        "ZAR" : "Zapotlán del Rey",
        "ZAG" : "Zapotlán el Grande",
        "ZAPT" : "Zapotlanejo", 
    }
    direccion = models.CharField(max_length=100)
    colonia = models.CharField(max_length=50)
    municipio = models.CharField(max_length=5,choices=MUNICIPIO)
    region = models.CharField(max_length=3, choices=REGION)
    id_usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    miembros_domicilio = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Número de personas que viven en el domicilio"
    )
    
    def __str__(self):
        return self.direccion#concatenar en el panel de administrador
    

class consumoagua(models.Model):#Tabla de consumos
    REPORTE = (
        ("SEM", "SEMANAL"),
        ("MES", "MENSUAL"),
    )
    TIPO_CONSUMO = (
        ("DOMESTICO", "Doméstico"),
        ("GANADERO", "Ganadero"),
        ("AGRICOLA", "Agrícola"),
        ("INDUSTRIAL", "Industrial"),
        ("COMERCIAL_SERVICIOS", "Comercial / Servicios"),
        ("PUBLICO_URBANO", "Público / Urbano"),
        ("RECREATIVO", "Recreativo"),
        ("OTRO", "Otro"),
    )

    #Datos a guardar en la base de datos
    cantidad = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(99999999)])
    tipo_reporte = models.CharField(max_length=50, choices=REPORTE)
    fecha = models.DateField()
    id_usuario = models.ForeignKey(User,on_delete=models.CASCADE)
    id_domicilio = models.ForeignKey(domicilior,on_delete=models.CASCADE)
    tipo_consumo = models.CharField(
        max_length=30,
        choices=TIPO_CONSUMO,
        null=True,
        blank=True,
        help_text="Tipo general de consumo de agua"
    )
    
    def __str__(self):
        return  f"{self.cantidad} m3 por {self.id_usuario.username}"#concatenar en el panel de admistrador
    
class recomendaciones(models.Model):#Tabla de recomendaciones
    ALGORITMOS = (
        ('regresion', 'Regresión'),
        ('bayes', 'Naive Bayes'),
        ('kmeans', 'K-Means'),
        ('general', 'General'), 
    )
    texto = models.CharField(max_length=500)
    fecha = models.DateField(default=timezone.now)
    id_usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    algoritmo = models.CharField(max_length=20, choices=ALGORITMOS, default='general')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['id_usuario', 'algoritmo', 'fecha'],
                name='uniq_rec_usuario_algoritmo_fecha'
            )
        ]

    def __str__(self):
        return f'{self.id_usuario.username} - {self.algoritmo} - {self.fecha}'


class RegresionMetricas(models.Model):#Tabla para guardar los datos del algorimto de regresion
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    fecha_entrenamiento = models.DateTimeField(auto_now_add=True)
    r2 = models.FloatField()
    mse = models.FloatField()
    b0 = models.FloatField()
    b1 = models.FloatField()
    prediccion = models.FloatField()

    def __str__(self):
        user_display = self.usuario.username if self.usuario else "Global"
        return f"Métricas {user_display} - {self.fecha_entrenamiento.strftime('%d/%m/%Y %H:%M')}"

class ClasificacionBayes(models.Model):#Tabla par guardar los datos del algoritmo de Bayes
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    consumo = models.FloatField()
    categoria = models.CharField(max_length=50)
    fecha_prediccion = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.usuario.username} - {self.categoria} ({self.consumo} m³)"

class EntrenamientoBayes(models.Model):#Tabla para reentrenar el modelo anterior
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_entrenamiento = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha_entrenamiento.strftime('%Y-%m-%d %H:%M')}"

class KMeansResultado(models.Model):#Tabla para guardar los datos del algoritmo de Kmeans
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    cluster = models.IntegerField()
    promedio_consumo = models.FloatField()
    fecha_analisis = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - Cluster {self.cluster}"


class Foto(models.Model): #Modelo para las fotos 
    titulo = models.CharField(max_length=100, blank=True, null=True)
    imagen = models.ImageField(upload_to="carrusel/")
    descripcion = models.TextField(blank=True, null=True)
    orden = models.PositiveBigIntegerField(default=0, help_text="Orden del carrusel")
    activo = models.BooleanField(default=True, help_text="Mostrar en carrusel")

    class Meta:
        ordering = ["orden"]   
        verbose_name = "Foto de carrusel"
        verbose_name_plural = "Fotos del carrusel" 
    def __str__(self):
        return self.titulo if self.titulo else f"Foto{self.id}"