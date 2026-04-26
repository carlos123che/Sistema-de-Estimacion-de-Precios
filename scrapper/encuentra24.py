import cloudscraper
from bs4 import BeautifulSoup
import time
import db_config
import data_cleaner

def extraer_detalle_encuentra24(scraper, url_detalle):
    """Entra a la página de la propiedad y extrae los datos completos."""
    print(f"  -> Extrayendo detalle: {url_detalle}")
    try:
        response = scraper.get(url_detalle)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Selectores precisos basados en el HTML proporcionado
        titulo = "N/A"
        h1 = soup.find('h1')
        if h1: titulo = h1.text.strip()
        
        # Extracción de Precio
        precio = "N/A"
        # Buscamos el div que contiene el símbolo $ y tiene clases de tamaño de texto
        precio_tag = soup.find('div', class_=re.compile(r'text-2xl|text-3xl|font-bold'))
        if precio_tag and '$' in precio_tag.text:
            precio = precio_tag.text.strip()
        
        ubicacion = "N/A"
        # Selector de ubicación (generalmente cerca del título o en el subtitle)
        ubi_tag = soup.find('p', class_='card_subtitle') or soup.find('span', class_='location')
        if ubi_tag: ubicacion = ubi_tag.text.strip()
        
        # Características físicas (Recámaras, Baños, Área, Parking)
        habitaciones = "0"
        banos = "0"
        parqueos = "0"
        area = "0"
        
        # Buscamos todos los bloques de especificaciones
        # Cada especificación tiene un span con el nombre (recámaras, baños, etc) y otro con el valor
        bloques = soup.find_all('div', class_=re.compile(r'flex-col items-start'))
        for bloque in bloques:
            label_tag = bloque.find('span', class_=re.compile(r'text-xs'))
            value_tag = bloque.find('span', class_=re.compile(r'text-\[20px\]|font-semibold'))
            
            if label_tag and value_tag:
                label = label_tag.text.lower()
                valor = value_tag.text.strip()
                
                if 'recámara' in label or 'habitación' in label:
                    habitaciones = valor
                elif 'baño' in label:
                    banos = valor
                elif 'parking' in label or 'estacionamiento' in label or 'parqueo' in label:
                    parqueos = valor
                elif 'área' in label or 'construida' in label or 'm²' in label:
                    area = valor
        
        # Respaldo por si no encontró con los selectores anteriores (búsqueda por texto en toda la página)
        if habitaciones == "0" or banos == "0" or area == "0":
            todos_los_spans = soup.find_all('span')
            for i, s in enumerate(todos_los_spans):
                t = s.text.lower()
                if 'recámara' in t and i+1 < len(todos_los_spans):
                    habitaciones = todos_los_spans[i+1].text.strip()
                elif 'baño' in t and i+1 < len(todos_los_spans):
                    banos = todos_los_spans[i+1].text.strip()
                elif 'parking' in t and i+1 < len(todos_los_spans):
                    parqueos = todos_los_spans[i+1].text.strip()
                elif ('área' in t or 'construida' in t) and i+1 < len(todos_los_spans):
                    area = todos_los_spans[i+1].text.strip()

        return {
            "Titulo": titulo,
            "Precio_Crudo": precio,
            "Ubicacion": ubicacion,
            "Habitaciones": habitaciones,
            "Banos": banos,
            "Parqueos": parqueos,
            "Area_m2": area,
            "URL": url_detalle
        }
    except Exception as e:
        print(f"      Error en detalle: {e}")
        return None

def scraper_encuentra24():
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    
    total_procesados = 0
    
    # Loop de páginas 1 a 59
    for i in range(1, 60):
        if i == 1:
            url_indice = "https://www.encuentra24.com/guatemala-es/bienes-raices-venta-de-propiedades-casas/guatemala-guatemala-city"
        else:
            url_indice = f"https://www.encuentra24.com/guatemala-es/bienes-raices-venta-de-propiedades-casas.{i}/guatemala-guatemala-city"
        
        print(f"\n--- ESCANEANDO PÁGINA {i}: {url_indice} ---")
        
        try:
            response = scraper.get(url_indice)
            if response.status_code != 200:
                print(f"Error {response.status_code} en página {i}. Saltando...")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extraer todos los links de las tarjetas de propiedades
            enlaces = soup.find_all('a', class_='item-card-link')
            
            if not enlaces:
                print("No se encontraron enlaces en esta página.")
                continue
                
            for e in enlaces:
                href = e.get_attribute_list('href')[0]
                if not href: continue
                url_detalle = "https://www.encuentra24.com" + href if href.startswith('/') else href
                
                # Entramos al detalle de la propiedad
                detalles = extraer_detalle_encuentra24(scraper, url_detalle)
                
                if detalles:
                    # Inserción en Base de Datos
                    conn = db_config.get_connection()
                    if conn:
                        try:
                            id_fuente = db_config.get_or_create_fuente(conn, "Encuentra24", "https://www.encuentra24.com")
                            id_tipo_inmueble = db_config.get_or_create_tipo_inmueble(conn, "Casa")
                            
                            nombre_zona = data_cleaner.extraer_zona(detalles['Ubicacion'])
                            id_zona_db = db_config.get_or_create_zona(conn, nombre_zona)
                            
                            precio_limpio = data_cleaner.limpiar_precio_quetzales(detalles['Precio_Crudo'])
                            area_limpia = data_cleaner.limpiar_area_metros(detalles['Area_m2'])
                            habs_limpio = data_cleaner.limpiar_entero(detalles['Habitaciones'])
                            banos_limpio = data_cleaner.limpiar_decimal(detalles['Banos'])
                            parq_limpio = data_cleaner.limpiar_entero(detalles['Parqueos'])
                            
                            datos_db = {
                                'id_fuente': id_fuente,
                                'id_zona': id_zona_db,
                                'id_tipo_inmueble': id_tipo_inmueble,
                                'precio_quetzales': precio_limpio,
                                'area_metros': area_limpia,
                                'habitaciones': habs_limpio,
                                'baños': banos_limpio,
                                'parqueos': parq_limpio
                            }
                            db_config.insert_inmueble(conn, datos_db)
                            total_procesados += 1
                        except Exception as e_db:
                            print(f"        Error DB: {e_db}")
                        finally:
                            conn.close()
                
                # Pausa obligatoria por propiedad (5 segundos según usuario)
                time.sleep(5)
                
        except Exception as ex:
            print(f"Error en página {i}: {ex}")

    return total_procesados

# ==========================================
# EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    import re
    
    total = scraper_encuentra24()
    
    print(f"\n¡Éxito total! Se procesaron y enviaron {total} propiedades a la base de datos.")