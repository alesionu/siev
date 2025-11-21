Sistema Inteligente de Estimación de Viviendas (SIEV)

Este es un prototipo de un sistema web para la estimación de proyectos de viviendas unifamiliares. La aplicación utiliza Machine Learning para predecir costos, programa arquitectónico y sugerir una distribución conceptual.

Arquitectura del Prototipo

El sistema utiliza un backend de Django y una arquitectura de dos modelos de Machine Learning (ML) para procesar las entradas del usuario.

Modelo 1: Regresión

Tipo: RandomForestRegressor (Scikit-learn).

Propósito: Este modelo predice todos los valores numéricos del proyecto.

Entradas: m2_terreno, cantidad_personas, orientacion, forma_terreno.

Salidas (Predicciones):

costo_estimado

tiempo_meses

cantidad_dormitorio

cantidad_bano

m2_cocina, m2_estar_comedor, etc.

Modelo 2: (Clasificación - Simulado)

Tipo: RandomForestClassifier (de Scikit-learn).

Propósito: Este modelo simula la generación de un plano. En lugar de dibujar un plano, este modelo actúa como un "seleccionador inteligente".

Entradas: Las mismas que el Modelo 1.

Salida (Predicción):

Un "apodo" o "llave" (ej. 3-dorm-compacto) que identifica cuál de los planos estáticos pre-dibujados es el más adecuado para la solicitud del usuario.

El backend (Django) luego toma estas dos predicciones, las combina y las envía al frontend (JavaScript) para mostrarlas al usuario.

Cómo Instalar y Correr el Proyecto

Sigue estos pasos para ejecutar el proyecto en tu máquina local.

1. Prerrequisitos

Python 3.10+

Git (opcional, si clonas el repositorio)

2. Configuración del Entorno

1. Clona este repositorio o descarga el ZIP y descomprímelo
git clone https://...

2. Entra en la carpeta del proyecto
cd sistema_estimador

3. Crea un entorno virtual
python -m venv venv

4. Activa el entorno virtual
En Windows:
.\venv\Scripts\activate
En Mac/Linux:
source venv/bin/activate


3. Instalación de Dependencias

5. Instala todas las librerías necesarias
pip install -r requirements.txt


4. Entrenamiento de la IA (Solo se hace una vez)

6. Ejecuta el script de entrenamiento.
Esto leerá 'datos_proyecto.csv' y creará los archivos .joblib
python train_models.py


5. Ejecución del Servidor

 7. Inicia el servidor de Django
python manage.py runserver

 8. Abre tu navegador
 Ve a [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
