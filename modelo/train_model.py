import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# Cargar variables de entorno desde el archivo .env
load_dotenv()

def get_connection():
    """Establece conexión con la base de datos PostgreSQL usando variables de entorno."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            dbname=os.getenv("DB_NAME", "bienes_raices_db"),
            port=os.getenv("DB_PORT", "5432")
        )
        return conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def load_data():
    """Extrae los datos de la base de datos y los carga en un DataFrame de Pandas."""
    conn = get_connection()
    if conn is None:
        return None
    
    query = """
    SELECT 
        z.nombre_zona as zona, 
        ti.nombre_tipo_inmueble as tipo_inmueble, 
        i.area_metros, 
        i.habitaciones, 
        i.baños, 
        i.parqueos, 
        i.precio_quetzales as precio
    FROM Inmueble i
    JOIN Zona z ON i.id_zona = z.id_zona
    JOIN Tipo_Inmueble ti ON i.id_tipo_inmueble = ti.id_tipo_inmueble
    WHERE i.precio_quetzales IS NOT NULL 
      AND i.precio_quetzales > 0;
    """
    
    print("Ejecutando consulta en la base de datos...")
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def train():
    print("--- Inicio de Entrenamiento del Modelo ---")
    df = load_data()
    
    if df is None or df.empty:
        print("No se encontraron datos para entrenar. Asegúrate de que el scrapper haya poblado la base de datos.")
        return

    # Limpieza básica: Eliminar filas con valores nulos en las columnas críticas
    # El precio ya viene filtrado desde el SQL, pero filtramos las demás por seguridad
    df = df.dropna(subset=['zona', 'tipo_inmueble', 'area_metros', 'habitaciones', 'baños', 'parqueos'])
    
    print(f"Datos cargados exitosamente: {len(df)} registros válidos.")
    
    # Definir características (X) y objetivo (y)
    X = df.drop('precio', axis=1)
    y = df['precio']
    
    # Identificar columnas categóricas y numéricas
    categorical_features = ['zona', 'tipo_inmueble']
    numerical_features = ['area_metros', 'habitaciones', 'baños', 'parqueos']
    
    # Crear el preprocesador:
    # 1. StandardScaler para normalizar los valores numéricos
    # 2. OneHotEncoder para convertir categorías en variables numéricas (dummy variables)
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])
    
    # Crear el Pipeline: Preprocesamiento + Modelo de Regresión
    # Usamos RandomForestRegressor por su robustez ante datos de mercado inmobiliario
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=150, random_state=42))
    ])
    
    # Dividir en sets de entrenamiento y prueba (80/20)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Entrenando el modelo (esto puede tardar un momento)...")
    model.fit(X_train, y_train)
    
    # Evaluación del modelo
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print("\n--- Resultados de la Evaluación ---")
    print(f"Error Medio Absoluto (MAE): Q {mae:,.2f}")
    print(f"Precisión (R² Score): {r2:.4f}")
    
    # Guardar el modelo entrenado
    model_filename = 'modelo_precio_inmuebles.pkl'
    print(f"\nGuardando el modelo en '{model_filename}'...")
    joblib.dump(model, model_filename)
    
    # También guardamos las columnas de entrenamiento para asegurar consistencia en la predicción futura
    joblib.dump(X.columns.tolist(), 'features_list.pkl')
    
    print("Entrenamiento completado y modelo guardado con éxito.")

if __name__ == "__main__":
    train()
