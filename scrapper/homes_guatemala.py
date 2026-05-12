import requests
import db_config
import data_cleaner
import time

# --- NUEVA CONFIGURACIÓN API DESCUBIERTA ---
API_BASE_URL = "https://app-pool.vylaris.com.ar/homes/api/Inmueble"
HEADERS = {
    "Origin": "https://homesguatemala.com",
    "Referer": "https://homesguatemala.com/",
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("Iniciando extracción desde la NUEVA API de Homes Guatemala...")

conn = db_config.get_connection()
if conn:
    id_fuente = db_config.get_or_create_fuente(conn, "Homes Guatemala", "https://homesguatemala.com")
    id_tipo_inmueble_base = db_config.get_or_create_tipo_inmueble(conn, "Inmueble")
else:
    print("Advertencia: No se pudo conectar a la base de datos.")

total_procesados = 0

# El usuario pidió de la página 1 a la 6
for page in range(1, 7):
    print(f"Consultando página {page}...")
    params = {
        "PageNumber": page,
        "PageSize": 12, # Tamaño estándar por página
        "Operaciones": "Venta"
    }
    
    try:
        # Petición a la nueva URL
        response = requests.get(API_BASE_URL, headers=HEADERS, params=params)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            print(f"  - Encontrados {len(items)} inmuebles.")
            
            for item in items:
                titulo = item.get("titulo", "Sin título")
                ubicacion = item.get("ubicaciones", "Sin ubicación")
                precio = item.get("precio", 0)
                habs = item.get("habitaciones", 0)
                banos = item.get("banos", 0)
                parqueos = item.get("parqueos", 0)
                area = item.get("metrosCuadrados", 0)
                tipo_str = item.get("tipos", "Inmueble")
                
                # Extraer o construir URL
                url_propiedad = item.get("url") or item.get("seoUrl")
                if not url_propiedad:
                    id_prop = item.get("id") or item.get("inmuebleId") or ""
                    url_propiedad = f"https://homesguatemala.com/propiedad/{id_prop}" if id_prop else "https://homesguatemala.com/"

                # Insercion DB
                if conn:
                    try:
                        precio_con_moneda = f"$ {precio}"
                        precio_db = data_cleaner.limpiar_precio_quetzales(precio_con_moneda)
                        
                        nombre_zona = data_cleaner.extraer_zona(ubicacion)
                        id_zona_db = db_config.get_or_create_zona(conn, nombre_zona)
                        
                        # Determinar tipo de inmueble
                        id_tipo_inmueble = id_tipo_inmueble_base
                        if tipo_str:
                            id_tipo_inmueble = db_config.get_or_create_tipo_inmueble(conn, tipo_str)
                        
                        datos_db = {
                            'id_fuente': id_fuente,
                            'id_zona': id_zona_db,
                            'id_tipo_inmueble': id_tipo_inmueble,
                            'precio_quetzales': precio_db,
                            'area_metros': area,
                            'habitaciones': habs,
                            'baños': banos,
                            'parqueos': parqueos,
                            'url': url_propiedad
                        }
                        db_config.insert_inmueble(conn, datos_db)
                        total_procesados += 1
                    except Exception as e_db:
                        print(f"    - Error al insertar {titulo}: {e_db}")
        else:
            print(f"  - Error en la API (página {page}): {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"  - Excepción en página {page}: {e}")
    
    # Pequeño delay para no saturar el servidor
    time.sleep(1)

print(f"\n¡Extracción finalizada! Se procesaron {total_procesados} propiedades en total.")

if conn:
    conn.close()