from django.shortcuts import render
import os
import joblib
import pandas as pd
from django.conf import settings
import psycopg
from dotenv import load_dotenv

# Cargar variables de entorno (del archivo .env en modelo/)
dotenv_path = os.path.join(settings.BASE_DIR, 'modelo', '.env')
load_dotenv(dotenv_path)

# Cargar el modelo al iniciar (asumiendo que está en web/modelo)
MODEL_PATH = os.path.join(settings.BASE_DIR, 'modelo', 'modelo_precio_inmuebles.pkl')
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"No se pudo cargar el modelo: {e}")
    model = None

def predict_price(zona, tipo_inmueble, area_metros, habitaciones, banos, parqueos):
    if not model:
        return None
    try:
        input_data = pd.DataFrame([{
            'zona': zona,
            'tipo_inmueble': tipo_inmueble,
            'area_metros': float(area_metros),
            'habitaciones': int(habitaciones),
            'baños': float(banos),
            'parqueos': int(parqueos)
        }])
        # Característica necesaria para el nuevo modelo
        input_data['area_por_habitacion'] = input_data['area_metros'] / (input_data['habitaciones'] + 1)
        
        return model.predict(input_data)[0]
    except Exception as e:
        print(f"Error prediciendo: {e}")
        return None

def get_similar_properties(estimacion, zona_limpia):
    propiedades = []
    try:
        conn = psycopg.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            dbname=os.getenv("DB_NAME", "bienes_raices_db"),
            port=os.getenv("DB_PORT", "5432")
        )
        with conn.cursor() as cur:
            query = """
                SELECT 
                    ti.nombre_tipo_inmueble, 
                    z.nombre_zona, 
                    i.area_metros, 
                    i.habitaciones, 
                    i.baños, 
                    i.parqueos, 
                    i.precio_quetzales,
                    i.url
                FROM Inmueble i
                JOIN Zona z ON i.id_zona = z.id_zona
                JOIN Tipo_Inmueble ti ON i.id_tipo_inmueble = ti.id_tipo_inmueble
                WHERE i.precio_quetzales > 0
                ORDER BY 
                    (CASE WHEN z.nombre_zona = %s THEN 0 ELSE 1 END),
                    ABS(i.precio_quetzales - %s) ASC
                LIMIT 15;
            """
            cur.execute(query, (zona_limpia, estimacion))
            rows = cur.fetchall()
            
            imagenes = [
                'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1518780664697-55e3ad937233?auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1600607687931-570a2569eb2e?auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=800&q=80'
            ]
            
            for i, row in enumerate(rows):
                propiedades.append({
                    'titulo': f'{row[0]} en {row[1]}',
                    'ubicacion': row[1],
                    'area': f'{row[2]} m²',
                    'habs': f'{row[3]} Hab.',
                    'banos': f'{row[4]} Baños',
                    'parq': f'{row[5]} Parq.',
                    'precio': f'Q {row[6]:,.2f}',
                    'tipo': 'SIMILAR',
                    'imagen': imagenes[i % len(imagenes)],
                    'url': row[7] if len(row) > 7 and row[7] else '#'
                })
        conn.close()
    except Exception as e:
        print(f"Error fetching similar properties: {e}")
    return propiedades

def index(request):
    propiedades_referencia = []
    
    # Obtener zonas desde la base de datos
    zonas = []
    try:
        conn = psycopg.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            dbname=os.getenv("DB_NAME", "bienes_raices_db"),
            port=os.getenv("DB_PORT", "5432")
        )
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT nombre_zona FROM Zona WHERE nombre_zona != 'Otra' ORDER BY nombre_zona")
            zonas = [row[0] for row in cur.fetchall()]
        conn.close()
    except Exception as e:
        print(f"Error cargando zonas de DB: {e}")
        # Fallback por si la DB falla
        zonas = ["Zona 10", "Zona 14", "Zona 15", "Zona 16"]

    precio_estimado_str = 'Q 0.00'
    mostrar_resultados = False

    if request.method == 'POST':
        zona = request.POST.get('zona')
        area = request.POST.get('area')
        habitaciones = request.POST.get('habitaciones')
        banos = request.POST.get('banos')
        parqueos = request.POST.get('parqueos')
        tipo_inmueble = 'Apartamento' # Valor por defecto ya que no está en el form actual
        
        # El modelo fue entrenado con "Zona 10", no "Zona 10, Ciudad de Guatemala"
        zona_limpia = zona.split(',')[0].strip() if zona else ""
        
        if area and habitaciones and banos and parqueos:
            print(f"--- Solicitando predicción ---")
            print(f"Datos de entrada -> Zona: {zona_limpia}, Tipo: {tipo_inmueble}, Área: {area}, Habs: {habitaciones}, Baños: {banos}, Parq: {parqueos}")
            estimacion = predict_price(zona_limpia, tipo_inmueble, area, habitaciones, banos, parqueos)
            if estimacion:
                print(f"==== RESULTADO DEL MODELO: Q {estimacion:,.2f} ====")
                precio_estimado_str = f"Q {estimacion:,.2f}"
                mostrar_resultados = True
                
                # Convertir numpy.float64 a float nativo de Python para que  no falle
                estimacion_float = float(estimacion)
                propiedades_referencia = get_similar_properties(estimacion_float, zona_limpia)
            else:
                print("El modelo devolvió None o falló.")

    context = {
        'propiedades': propiedades_referencia,
        'zonas': zonas,
        'precio_estimado': precio_estimado_str,
        'mostrar_resultados': mostrar_resultados
    }
    
    return render(request, 'estimator/index.html', context)
