from django.db import models
from django.contrib.auth.models import User#importando la tabla usuario para la relacion

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
    
    def __str__(self):
        return self.direccion + ' por ' + self.id_usuario.username #concatenar en el panel de administrador
    

class consumoagua(models.Model):#Tabla de consumos
    REPORTE = {
        "SEM" : "SEMANAL",
        "MES" : "MENSUAL",
    }
    cantidad = models.BigIntegerField()
    tipo_reporte = models.CharField(max_length=50, choices=REPORTE)
    fecha = models.DateField()
    id_usuario = models.ForeignKey(User,on_delete=models.CASCADE)
    id_domicilio = models.ForeignKey(domicilior,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.cantidad + ' m3 ' + ' por ' + self.id_usuario.username #concatenar en el panel de admistrador
    

class recomendaciones(models.Model): #Tabla recomendaciones
    texto = models.CharField(max_length=500)
    fecha = models.DateField()
    id_usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.texto + ' para ' + self.id_usuario.username #concatenar en el panel de admistrador


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