import cloudscraper
from bs4 import BeautifulSoup
import time
import re
import db_config
import data_cleaner 

# Configuración inicial
URL_PRINCIPAL = "https://fha.gob.gt/casas/nuevas?departamentoID=1"
BASE_URL = "https://fha.gob.gt"

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
)

conn = db_config.get_connection()
if conn:
    id_fuente = db_config.get_or_create_fuente(conn, "FHA", "https://fha.gob.gt")
    id_tipo_inmueble = db_config.get_or_create_tipo_inmueble(conn, "Casa")
else:
    print("Advertencia: No se pudo conectar a la base de datos.")

def extraer_caracteristica(soup_obj, etiqueta):
    nodo_etiqueta = soup_obj.find(lambda tag: tag.name == "p" and etiqueta in tag.text)
    if nodo_etiqueta:
        nodo_valor = nodo_etiqueta.find_next_sibling("p")
        if nodo_valor:
            return " ".join(nodo_valor.text.split())
    return None

urls_detalles = []

for page in range(1, 5):
    url_con_pagina = f"{URL_PRINCIPAL}&page={page}"
    print(f"Mapeando página {page}: {url_con_pagina}...")
    try:
        response = scraper.get(url_con_pagina)
        if response.status_code == 200:
            soup_index = BeautifulSoup(response.text, "html.parser")
            enlaces = soup_index.find_all("a", href=re.compile(r"nuevas/\d+"))
            urls_pagina = []
            for link in enlaces:
                href = link['href']
                if not href.startswith('http'):
                    if not href.startswith('/'):
                        href = "/casas/" + href
                    href = BASE_URL + href
                urls_pagina.append(href)
            urls_detalles.extend(urls_pagina)
            print(f"  - Encontrados: {len(urls_pagina)}")
        else:
            print(f"  - Error al acceder a la página {page}: {response.status_code}")
    except Exception as e:
        print(f"  - Error en página {page}: {e}")
    
    time.sleep(1)

urls_detalles = list(set(urls_detalles))
print(f"\nTotal de URLs únicas a extraer: {len(urls_detalles)}\n")

dataset_casas = []

for i, url in enumerate(urls_detalles):
    print(f"[{i+1}/{len(urls_detalles)}] Extrayendo: {url}")
    
    try:
        resp_casa = scraper.get(url)
        
        if resp_casa.status_code == 200:
            soup_casa = BeautifulSoup(resp_casa.text, "html.parser")
            
            id_caso = url.split('/')[-1]
            
            registro = {
                "ID_Caso": id_caso,
                "URL": url,
                "Precio (Q)": extraer_caracteristica(soup_casa, "Precio desde:"),
                "Enganche (Q)": extraer_caracteristica(soup_casa, "Enganche desde:"),
                "Cuota (Q)": extraer_caracteristica(soup_casa, "Cuota desde:"),
                "Habitaciones": extraer_caracteristica(soup_casa, "Habitaciones:"),
                "Baños": extraer_caracteristica(soup_casa, "Baños"),
                "Parqueos": extraer_caracteristica(soup_casa, "Parqueos:"),
                "Dirección": extraer_caracteristica(soup_casa, "Dirección:"),
                "Construcción": extraer_caracteristica(soup_casa, "Construcción")
            }
            
            dataset_casas.append(registro)

            # Insertar en base de datos
            if conn:
                try:
                    precio_str = registro["Precio (Q)"]
                    precio_limpio = data_cleaner.limpiar_precio_quetzales(precio_str)
                    
                    area_str = registro["Construcción"]
                    area_limpia = data_cleaner.limpiar_area_metros(area_str)
                    
                    # Para 'nuevas', los campos son directos
                    habs_limpio = data_cleaner.limpiar_entero(registro["Habitaciones"])
                    banos_limpio = data_cleaner.limpiar_entero(registro["Baños"])
                    parqueos_limpio = data_cleaner.limpiar_entero(registro["Parqueos"])
                    
                    # Extraer zona de la dirección
                    nombre_zona = data_cleaner.extraer_zona(registro["Dirección"])
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
                        'url': url
                    }
                    db_config.insert_inmueble(conn, datos_db)
                except Exception as e_db:
                    print(f"Error al insertar en BD: {e_db}")

        else:
            print(f"  -> Código de error {resp_casa.status_code} al acceder.")
            
    except Exception as e:
        print(f"  -> Ocurrió un error con esta URL: {e}")
        
    time.sleep(2) 
    
print("\nExtracción finalizada")
print(f"Total de registros procesados: {len(dataset_casas)}")

if conn:
    conn.close()