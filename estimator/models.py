from django.db import models
from django.contrib.auth.models import User

class Estimation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=100, default="Mi Estimación")
    created_at = models.DateTimeField(auto_now_add=True)

    input_m2_terreno = models.FloatField()
    input_cantidad_personas = models.IntegerField()
    input_orientacion = models.IntegerField()
    input_forma_terreno = models.CharField(max_length=50)

    result_cantidad_dormitorio = models.IntegerField()
    result_cantidad_bano = models.IntegerField()
    result_m2_cocina = models.FloatField()
    result_m2_estar_comedor = models.FloatField()
    result_m2_dormitorios_total = models.FloatField()
    result_m2_banos_total = models.FloatField()
    result_costo_estimado = models.FloatField()
    result_tiempo_meses = models.FloatField()
    


    result_layout_key = models.CharField(max_length=100)

    def __str__(self):
        return f"'{self.project_name}' de {self.user.username}"