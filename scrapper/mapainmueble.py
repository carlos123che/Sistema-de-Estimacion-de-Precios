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

# Iterar de la página 1 a la 114
for page in range(1, 115):
    url = BASE_URL if page == 1 else f"{BASE_URL}?page={page}"
    print(f"\nMapeando página {page}: {url}...")
    
    try:
        response = scraper.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. NUEVA BÚSQUEDA DE TARJETAS: Buscamos las etiquetas <a> que envuelven toda la casa
            tarjetas = soup.select('div.grid > a.group.block.bg-white')
            print(f"  - Encontradas {len(tarjetas)} propiedades.")
            
            for tarjeta in tarjetas:
                # 2. Extraer Título y Link
                titulo_tag = tarjeta.find('h3')
                titulo = titulo_tag.text.strip() if titulo_tag else 'N/A'
                
                # El link ahora viene incompleto (/propiedades/CVC...), le sumamos el dominio
                link_parcial = tarjeta.get('href', '')
                link = f"https://mapainmueble.com{link_parcial}" if link_parcial else 'N/A'
                
                # 3. Extraer Precio (Buscando la clase text-xl font-black)
                precio_tag = tarjeta.find('span', class_=lambda c: c and 'text-xl' in c and 'font-black' in c)
                precio = precio_tag.text.strip() if precio_tag else 'N/A'
                
                # 4. Extraer Ubicación
                loc_tag = tarjeta.find('span', class_='truncate')
                ubicacion = loc_tag.text.strip() if loc_tag else 'N/A'
                
                # 5. Extraer Detalles directamente de los íconos SVG de la tarjeta
                habs, banos, parqueos, area = 'N/A', 'N/A', None, 'N/A'
                
                # Buscamos todos los contenedores de íconos
                iconos = tarjeta.find_all('span', class_=lambda c: c and 'flex items-center gap-1' in c)
                
                for icono in iconos:
                    svg = icono.find('svg')
                    if svg:
                        clases_svg = " ".join(svg.get('class', []))
                        texto_icono = icono.text.strip()
                        
                        # Identificamos qué dato es basándonos en la clase del ícono
                        if 'lucide-bed-double' in clases_svg:
                            habs = texto_icono
                        elif 'lucide-bath' in clases_svg:
                            banos = texto_icono
                        elif 'lucide-car' in clases_svg:
                            parqueos = texto_icono
                        elif 'lucide-maximize' in clases_svg:
                            area = texto_icono
                
                # Inserción en BD (Esto se queda igual)
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
                            'parqueos': parqueos_limpio,
                            'url': link
                        }
                        db_config.insert_inmueble(conn, datos_db)
                        total_procesados += 1
                    except Exception as e_db:
                        print(f"    - Error al insertar {titulo}: {e_db}")
        else:
            print(f"  - Error en la página {page}: {response.status_code}")
            
    except Exception as e:
        print(f"  - Excepción en página {page}: {e}")
    
    # Redujimos el delay a 1 segundo porque ya no bombardeamos al servidor entrando a cada casa
    time.sleep(1)

print(f"\n¡Extracción finalizada! Se procesaron {total_procesados} propiedades en total.")

if conn:
    conn.close()