import cloudscraper
from bs4 import BeautifulSoup
import time
import db_config
import data_cleaner

# Configuración inicial
BASE_URL = "https://mapainmueble.com/casas-en-venta-guatemala/"

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
)

def extraer_dato_detalle(soup_detail, etiqueta):
    """Extrae un valor de la sección Detalles del inmueble."""
    items = soup_detail.select('.listing_detail')
    for item in items:
        strong = item.find('strong')
        if strong and etiqueta.lower() in strong.text.lower():
            # El valor es el texto del div menos el texto del strong
            return item.get_text(strip=True).replace(strong.text.strip(), "").strip()
    return None

conn = db_config.get_connection()
if conn:
    id_fuente = db_config.get_or_create_fuente(conn, "MapaInmueble", "https://mapainmueble.com")
    id_tipo_inmueble = db_config.get_or_create_tipo_inmueble(conn, "Casa")
else:
    print("Advertencia: No se pudo conectar a la base de datos.")

total_procesados = 0

# Iterar de la página 1 a la 25
for page in range(1, 26):
    url = BASE_URL if page == 1 else f"{BASE_URL}page/{page}/"
    print(f"\nMapeando página {page}: {url}...")
    
    try:
        response = scraper.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            tarjetas = soup.find_all('div', class_='listing_wrapper')
            print(f"  - Encontradas {len(tarjetas)} propiedades.")
            
            for tarjeta in tarjetas:
                titulo = tarjeta.get('data-modal-title', 'N/A')
                link = tarjeta.get('data-modal-link', 'N/A')
                
                # Valores base del listado (como fallback)
                precio_tag = tarjeta.find('div', class_='listing_unit_price_wrapper')
                precio = precio_tag.text.strip() if precio_tag else 'N/A'
                
                loc_tag = tarjeta.find('div', class_='property_location_image')
                ubicacion = " ".join([a.text.strip() for a in loc_tag.find_all('a')]) if loc_tag else 'N/A'
                
                habs = 'N/A'
                banos = 'N/A'
                area = 'N/A'
                parqueos = None
                
                # Entrar al detalle para mayor precisión y parqueos
                if link and link != 'N/A':
                    print(f"    - Extrayendo detalle: {link}")
                    try:
                        resp_detail = scraper.get(link)
                        if resp_detail.status_code == 200:
                            soup_detail = BeautifulSoup(resp_detail.text, 'html.parser')
                            
                            # Extraer datos técnicos de la ficha detallada
                            d_habs = extraer_dato_detalle(soup_detail, "Habitaciones")
                            d_banos = extraer_dato_detalle(soup_detail, "Baños")
                            d_parqueos = extraer_dato_detalle(soup_detail, "Parqueos")
                            d_area = extraer_dato_detalle(soup_detail, "Metros² de Construcción")
                            
                            # Priorizar datos del detalle si existen
                            if d_habs: habs = d_habs
                            if d_banos: banos = d_banos
                            if d_parqueos: parqueos = d_parqueos
                            if d_area: area = d_area
                        else:
                            print(f"      ! Error detalle: {resp_detail.status_code}")
                    except Exception as e_detail:
                        print(f"      ! Error detalle: {e_detail}")
                    
                    # Delay para no ser bloqueados
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
                        
                        datos_db = {
                            'id_fuente': id_fuente,
                            'id_zona': id_zona_db,
                            'id_tipo_inmueble': id_tipo_inmueble,
                            'precio_quetzales': precio_limpio,
                            'area_metros': area_limpia,
                            'habitaciones': habs_limpio,
                            'baños': banos_limpio,
                            'parqueos': parqueos_limpio
                        }
                        db_config.insert_inmueble(conn, datos_db)
                        total_procesados += 1
                    except Exception as e_db:
                        print(f"    - Error al insertar {titulo}: {e_db}")
        else:
            print(f"  - Error en la página {page}: {response.status_code}")
            
    except Exception as e:
        print(f"  - Excepción en página {page}: {e}")
    
    # Delay entre páginas
    time.sleep(2)

print(f"\n¡Extracción finalizada! Se procesaron {total_procesados} propiedades en total.")

if conn:
    conn.close()