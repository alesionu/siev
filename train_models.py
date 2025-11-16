import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import joblib
import os

# --- 1. DEFINICIÓN DE CONSTANTES ---
# El "libro de texto" que creaste
DATA_FILE = 'datos_proyectos.csv'

# La carpeta donde guardaremos los "cerebros" (modelos entrenados)
MODEL_DIR = os.path.join('estimator', 'models')
MODEL_PATH_PROGRAM = os.path.join(MODEL_DIR, 'model_program.joblib')
MODEL_PATH_LAYOUT = os.path.join(MODEL_DIR, 'model_layout.joblib')

# --- 2. CARGAR LOS DATOS ---
print(f"Cargando datos desde {DATA_FILE}...")
try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    print(f"Error: No se encontró el archivo {DATA_FILE}.")
    print("Asegúrate de que el archivo CSV esté en la misma carpeta que este script.")
    exit()

print("Datos cargados. Ejemplo:")
print(df.head()) # Muestra las primeras 5 filas

# --- 3. PRE-PROCESAMIENTO ---
# La IA no entiende palabras como "Norte" o "cuadrado".
# 'get_dummies' convierte esas palabras en columnas numéricas (0 o 1).
# Por ejemplo, 'orientacion' se convertirá en 'orientacion_Norte', 'orientacion_Sur', etc.
print("Pre-procesando datos (convirtiendo texto a números)...")
# Usamos las 2 columnas de texto que definimos
categorical_cols = ['orientacion', 'forma_terreno']
df_processed = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

print("Datos procesados. Nuevas columnas:")
print(df_processed.columns)

# --- 4. SEPARAR PREGUNTAS (X) Y RESPUESTAS (Y) ---

# Definimos las "respuestas" (targets) que queremos predecir
TARGETS_REGRESSION = [
    'cantidad_dormitorio',
    'cantidad_bano',
    'm2_cocina',
    'm2_estar_comedor',
    'm2_dormitorios_total',
    'm2_banos_total',
    'costo_estimado',
    'tiempo_meses'
]

TARGET_CLASSIFICATION = 'layout_key_target'

# Las "respuestas" (Y) son las columnas que acabamos de definir
Y_reg = df_processed[TARGETS_REGRESSION]
Y_class = df_processed[TARGET_CLASSIFICATION]

# Las "preguntas" (X) son TODO LO DEMÁS.
# Tomamos la tabla procesada y quitamos las columnas de respuesta.
X = df_processed.drop(columns=TARGETS_REGRESSION + [TARGET_CLASSIFICATION])

print(f"Preguntas (X) para la IA (primeras filas):\n{X.head()}")
print(f"Respuestas de Regresión (Y_reg) (primeras filas):\n{Y_reg.head()}")
print(f"Respuestas de Clasificación (Y_class) (primeras filas):\n{Y_class.head()}")

# --- 5. ENTRENAR MODELO 1 (REGRESIÓN) ---
print("\nEntrenando Modelo 1 (Regresión: Costos, M2, Cantidades)...")
# n_estimators=100 significa que usará 100 "árboles de decisión" para votar.
# random_state=42 asegura que el resultado sea siempre el mismo si lo corremos de nuevo.
model_program = RandomForestRegressor(n_estimators=100, random_state=42, oob_score=True)

# ¡La magia! 'fit' es la orden de "estudiar" el libro de texto.
model_program.fit(X, Y_reg)

print(f"Modelo 1 (Regresión) entrenado. Puntuación OOB: {model_program.oob_score_:.4f}")

# --- 6. ENTRENAR MODELO 2 (CLASIFICACIÓN) ---
print("\nEntrenando Modelo 2 (Clasificación: Selección de Plano)...")
model_layout = RandomForestClassifier(n_estimators=100, random_state=42, oob_score=True)

# Le ordenamos estudiar las mismas preguntas (X) pero para adivinar el plano (Y_class)
model_layout.fit(X, Y_class)
print(f"Modelo 2 (Clasificación) entrenado. Puntuación OOB: {model_layout.oob_score_:.4f}")

# --- 7. GUARDAR LOS MODELOS "CEREBROS" ---
print("\nGuardando modelos en el disco...")

# Crear la carpeta 'estimator/models/' si no existe
os.makedirs(MODEL_DIR, exist_ok=True)
print(f"Directorio de modelos asegurado en: {MODEL_DIR}")

# 'joblib.dump' es como "congelar" el cerebro de la IA en un archivo.
joblib.dump(model_program, MODEL_PATH_PROGRAM)
print(f"Modelo 1 (Regresión) guardado en: {MODEL_PATH_PROGRAM}")

joblib.dump(model_layout, MODEL_PATH_LAYOUT)
print(f"Modelo 2 (Clasificación) guardado en: {MODEL_PATH_LAYOUT}")

print("\n--- ¡Proceso del Día 2 completado! ---")
print("Tus dos modelos de IA han sido entrenados y guardados.")