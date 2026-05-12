import cloudscraper
from bs4 import BeautifulSoup
import json
import time
import db_config
import data_cleaner

# Configuración inicial
BASE_URL = "https://www.inversen.com"
SEARCH_URL = "https://www.inversen.com/properties/guatemala/guatemala/guatemala?web_page=properties&page="

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
)

def extraer_dato_tecnico(soup_detail, etiqueta):
    """Extrae un valor de la tabla de datos técnicos de EasyBroker."""
    items = soup_detail.select('.property-technical-data-item')
    for item in items:
        dt = item.find('dt')
        dd = item.find('dd')
        if dt and dd and etiqueta.lower() in dt.text.lower():
            return dd.text.strip()
    return None

conn = db_config.get_connection()
if conn:
    id_fuente = db_config.get_or_create_fuente(conn, "Inversen", "https://www.inversen.com")
    id_tipo_inmueble_base = db_config.get_or_create_tipo_inmueble(conn, "Inmueble")
else:
    print("Advertencia: No se pudo conectar a la base de datos.")

total_procesados = 0

# Iterar de la página 1 a la 42
for page in range(1, 43):
    url = f"{SEARCH_URL}{page}"
    print(f"\nMapeando página {page}: {url}...")
    
    try:
        response = scraper.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            propiedades = soup.find_all('div', class_='property-listing')
            print(f"  - Encontradas {len(propiedades)} propiedades.")
            
            for prop in propiedades:
                popover_str = prop.get('data-popover-data')
                
                if popover_str:
                    try:
                        info = json.loads(popover_str)
                        
                        titulo = info.get('title', 'N/A')
                        url_relativa = info.get('url', '')
                        url_completa = f"{BASE_URL}{url_relativa}" if url_relativa else None
                        
                        # Valores base del JSON (como fallback)
                        precio = info.get('price', 'N/A')
                        ubicacion = info.get('location', 'N/A')
                        habs = info.get('bedrooms', 'N/A')
                        banos = info.get('bathrooms', 'N/A')
                        area = info.get('size', 'N/A')
                        parqueos = None
                        
                        # Entrar al detalle para mayor precisión y parqueos
                        if url_completa:
                            print(f"    - Extrayendo detalle: {url_completa}")
                            try:
                                resp_detail = scraper.get(url_completa)
                                if resp_detail.status_code == 200:
                                    soup_detail = BeautifulSoup(resp_detail.text, 'html.parser')
                                    
                                    # Extraer datos técnicos precisos
                                    d_habs = extraer_dato_tecnico(soup_detail, "Dormitorios")
                                    d_banos = extraer_dato_tecnico(soup_detail, "Baños")
                                    d_parqueos = extraer_dato_tecnico(soup_detail, "Estacionamientos")
                                    d_area = extraer_dato_tecnico(soup_detail, "Superficie total")
                                    
                                    # Priorizar datos del detalle si existen
                                    if d_habs: habs = d_habs
                                    if d_banos: banos = d_banos
                                    if d_parqueos: parqueos = d_parqueos
                                    if d_area: area = d_area
                                    
                                else:
                                    print(f"      ! Error al acceder al detalle: {resp_detail.status_code}")
                            except Exception as e_detail:
                                print(f"      ! Error en detalle: {e_detail}")
                            
                            # Pequeño delay entre detalles para no ser bloqueados
                            time.sleep(1)
                        
                        # Inserción en BD
                        if conn:
                            try:
                                precio_limpio = data_cleaner.limpiar_precio_quetzales(precio)
                                area_limpia = data_cleaner.limpiar_area_metros(area)
                                habs_limpio = data_cleaner.limpiar_entero(habs)
                                banos_limpio = data_cleaner.limpiar_decimal(banos)
                                parqueos_limpio = data_cleaner.limpiar_entero(parqueos)
                                
                                nombre_zona = data_cleaner.extraer_zona(ubicacion)
                                id_zona_db = db_config.get_or_create_zona(conn, nombre_zona)
                                
                                tipo_inmueble = id_tipo_inmueble_base
                                if "apartamento" in titulo.lower() or "penthouse" in titulo.lower():
                                    tipo_inmueble = db_config.get_or_create_tipo_inmueble(conn, "Apartamento")
                                elif "casa" in titulo.lower() or "residencia" in titulo.lower():
                                    tipo_inmueble = db_config.get_or_create_tipo_inmueble(conn, "Casa")
                                elif "terreno" in titulo.lower():
                                    tipo_inmueble = db_config.get_or_create_tipo_inmueble(conn, "Terreno")
                                
                                datos_db = {
                                    'id_fuente': id_fuente,
                                    'id_zona': id_zona_db,
                                    'id_tipo_inmueble': tipo_inmueble,
                                    'precio_quetzales': precio_limpio,
                                    'area_metros': area_limpia,
                                    'habitaciones': habs_limpio,
                                    'baños': banos_limpio,
                                    'parqueos': parqueos_limpio,
                                    'url': url_completa
                                }
                                db_config.insert_inmueble(conn, datos_db)
                                total_procesados += 1
                            except Exception as e_db:
                                print(f"    - Error al insertar {titulo}: {e_db}")
                        
                    except json.JSONDecodeError:
                        print("    - Error decodificando JSON en una propiedad.")
        else:
            print(f"  - Error al acceder a la página {page}: {response.status_code}")
            
    except Exception as e:
        print(f"  - Excepción en página {page}: {e}")
    
    # Delay entre páginas
    time.sleep(2)

print(f"\n¡Extracción finalizada! Se procesaron e insertaron {total_procesados} propiedades.")

if conn:
    conn.close()