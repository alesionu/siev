import json
import joblib
import pandas as pd
import math
import os

from django.http import JsonResponse, HttpResponseBadRequest, Http404, HttpResponseRedirect
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Estimation

try:
    MODEL_PROGRAM_PATH = os.path.join(settings.BASE_DIR, 'estimator', 'models', 'model_program.joblib')
    MODEL_LAYOUT_PATH = os.path.join(settings.BASE_DIR, 'estimator', 'models', 'model_layout.joblib')
    MODEL_PROGRAM = joblib.load(MODEL_PROGRAM_PATH)
    MODEL_LAYOUT = joblib.load(MODEL_LAYOUT_PATH)
    print("Modelos de IA cargados exitosamente.")
except FileNotFoundError:
    print("Error: No se encontraron los archivos de modelo. Asegúrate de haber corrido 'train_models.py'")
    MODEL_PROGRAM = None
    MODEL_LAYOUT = None

MODEL_X_COLS = [
    'm2_terreno', 'cantidad_personas', 'orientacion_2', 'orientacion_3',
    'orientacion_4', 'forma_terreno_angosto', 'forma_terreno_cuadrado',
    'forma_terreno_irregular'
]
MODEL_Y_COLS_REG = [
    'cantidad_dormitorio', 'cantidad_bano', 'm2_cocina', 'm2_estar_comedor',
    'm2_dormitorios_total', 'm2_banos_total', 'costo_estimado', 'tiempo_meses'
]


def register_view(request):
    """
    Maneja el registro de usuarios nuevos.
    Usa el formulario UserCreationForm incorporado de Django.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'estimator/register.html', {'form': form})

@login_required
def dashboard_view(request):
    """
    Muestra el "Listado" de estimaciones.
    Esta es la nueva página principal (la raíz '/').
    """
    estimations = Estimation.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'estimations': estimations
    }
    return render(request, 'estimator/dashboard.html', context)

@login_required
def estimation_detail_view(request, estimation_id):
    """
    Muestra el detalle completo de una estimación guardada.
    """
    estimation = get_object_or_404(Estimation, id=estimation_id, user=request.user)
    
    context = {
        'estimation': estimation
    }
    return render(request, 'estimator/estimation_detail.html', context)

@login_required
def estimator_view(request):
    """
    Muestra la herramienta para crear una "Nueva Estimación".
    Esta página ahora vive en '/estimate/'.
    """
    return render(request, 'estimator/index.html')

@login_required
def delete_estimation_view(request, estimation_id):
    """
    Maneja la "Baja" (borrado) de una estimación.
    Solo acepta POST por seguridad.
    """
    if request.method == 'POST':
        estimation = get_object_or_404(Estimation, id=estimation_id, user=request.user)
        estimation.delete()
        return redirect('dashboard')
    else:
        return redirect('dashboard')

@login_required 
def estimation_detail_view(request, estimation_id):
 
    estimation = get_object_or_404(Estimation, id=estimation_id, user=request.user)
    
    context = {
        'estimation': estimation
    }
    
    return render(request, 'estimator/estimation_detail.html', context)


class ApiEstimateView(LoginRequiredMixin, View):
    
    
    def post(self, request, *args, **kwargs):
        if not MODEL_PROGRAM or not MODEL_LAYOUT:
            return JsonResponse({'error': 'Modelos no cargados en el servidor'}, status=500)

        try:
            data = json.loads(request.body)
            print(f"Datos JSON recibidos: {data}")
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Error: JSON mal formado.")

        try:
            input_df = self.preprocess_input(data)

            print("Consultando Modelo 1 (Regresión)...")
            program_pred = MODEL_PROGRAM.predict(input_df)

            print("Consultando Modelo 2 (Clasificación)...")
            layout_pred = MODEL_LAYOUT.predict(input_df)

            results_dict = self.format_output(program_pred, layout_pred)
            
            print(f"Respuesta JSON enviada: {results_dict}")
            return JsonResponse(results_dict)

        except KeyError as e:
            return HttpResponseBadRequest(f"Error: Falta el dato de entrada: {e}")
        except Exception as e:
            print(f"Error interno: {str(e)}")
            return JsonResponse({'error': f'Error interno del servidor: {str(e)}'}, status=500)

    def preprocess_input(self, data: dict) -> pd.DataFrame:
        
        processed_data = {col: 0 for col in MODEL_X_COLS}

        processed_data['m2_terreno'] = int(data['m2_terreno'])
        processed_data['cantidad_personas'] = int(data['cantidad_personas'])

        orientacion = int(data['orientacion'])
        if orientacion == 2:
            processed_data['orientacion_2'] = 1
        elif orientacion == 3:
            processed_data['orientacion_3'] = 1
        elif orientacion == 4:
            processed_data['orientacion_4'] = 1
        
        forma = data['forma_terreno']
        if forma == 'angosto':
            processed_data['forma_terreno_angosto'] = 1
        elif forma == 'cuadrado':
            processed_data['forma_terreno_cuadrado'] = 1
        elif forma == 'irregular':
            processed_data['forma_terreno_irregular'] = 1

        input_df = pd.DataFrame([processed_data])
        
        try:
            input_df = input_df[MODEL_X_COLS]
        except KeyError as e:
            print(f"Error: La columna {e} no se generó en preprocess_input.")
            raise e

        print(f"DataFrame pre-procesado para la IA:\n{input_df.to_string()}")
        return input_df

    def format_output(self, program_pred, layout_pred) -> dict:
        
        program_values = program_pred[0]
        layout_key = layout_pred[0]

        results = dict(zip(MODEL_Y_COLS_REG, program_values))

        results['cantidad_dormitorio'] = math.ceil(results['cantidad_dormitorio'])
        results['cantidad_bano'] = math.ceil(results['cantidad_bano'])
        results['costo_estimado'] = round(results['costo_estimado'], 2)
        results['tiempo_meses'] = round(results['tiempo_meses'], 1)
        results['m2_cocina'] = round(results['m2_cocina'], 1)
        results['m2_estar_comedor'] = round(results['m2_estar_comedor'], 1)
        results['m2_dormitorios_total'] = round(results['m2_dormitorios_total'], 1)
        results['m2_banos_total'] = round(results['m2_banos_total'], 1)
        
        results['url_plano_sugerido'] = f"estimator/{layout_key}.jpg" 

        return results


class ApiSaveEstimationView(LoginRequiredMixin, View):
   
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            print(f"Guardando estimación: {data}")
            
            required_fields = ['project_name', 'm2_terreno', 'cantidad_personas', 
                             'orientacion', 'forma_terreno', 'layout_key']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Falta el campo: {field}'}, status=400)
            
            estimation = Estimation.objects.create(
                user=request.user,
                project_name=data['project_name'],
                input_m2_terreno=data['m2_terreno'],
                input_cantidad_personas=data['cantidad_personas'],
                input_orientacion=data['orientacion'],
                input_forma_terreno=data['forma_terreno'],
                result_costo_estimado=data['costo_estimado'],
                result_tiempo_meses=data['tiempo_meses'],
                result_cantidad_dormitorio=data['cantidad_dormitorio'],
                result_cantidad_bano=data['cantidad_bano'],
                result_m2_cocina=data['m2_cocina'],
                result_m2_estar_comedor=data['m2_estar_comedor'],
                result_m2_dormitorios_total=data['m2_dormitorios_total'],
                result_m2_banos_total=data['m2_banos_total'],
                result_layout_key=data['layout_key']
            )
            
            print(f"¡Estimación '{data['project_name']}' guardada con ID: {estimation.id}!")
            
            return JsonResponse({
                'success': True,
                'message': 'Estimación guardada exitosamente',
                'estimation_id': estimation.id
            })
            
        except Exception as e:
            print(f"ERROR al guardar: {str(e)}")
            return JsonResponse({'error': f'Error al guardar: {str(e)}'}, status=500)