import cloudscraper
from bs4 import BeautifulSoup
import time
import db_config
import data_cleaner

# Configuración base
BASE_URL = "https://www.citymax-gt.com"
PAGINA_INICIAL = 1
PAGINA_FINAL = 11

# Nuestro 'disfraz' de navegador
scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
)

# Conexión a DB y preparativos
conn = db_config.get_connection()
if conn:
    id_fuente = db_config.get_or_create_fuente(conn, "CityMax", "https://www.citymax-gt.com")
    id_tipo_inmueble = db_config.get_or_create_tipo_inmueble(conn, "Casa")
else:
    print("Advertencia: No se pudo conectar a la base de datos.")

dataset_citymax = []

print("Iniciando barrido por páginas en CityMax...")
print("-" * 50)

# Loop para recorrer de la página 1 a la 11
for pagina in range(PAGINA_INICIAL, PAGINA_FINAL + 1):
    url_objetivo = f"{BASE_URL}/casas/venta/ciudad-de-guatemala?page={pagina}"
    print(f"Escaneando Página {pagina}: {url_objetivo}")
    
    try:
        response = scraper.get(url_objetivo)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Cada casa está contenida en una etiqueta <article>
            tarjetas = soup.find_all("article")
            
            if not tarjetas:
                print(f"  -> No se encontraron propiedades en la Página {pagina}.")
            else:
                print(f"  -> ¡Encontradas {len(tarjetas)} propiedades!")
                
                # Extraemos la data de cada tarjeta encontrada en esta zona
                for tarjeta in tarjetas:
                    # 1. Extraer URL
                    enlace_tag = tarjeta.find("a", href=True)
                    url_propiedad = BASE_URL + enlace_tag["href"] if enlace_tag else None
                    
                    # 2. Extraer Precio (Está en un span con texto grande)
                    precio_tag = tarjeta.find("span", class_=lambda c: c and "text-lg" in c)
                    precio = precio_tag.text.strip().replace("\t", " ") if precio_tag else None
                    
                    # 3. Extraer Ubicación (Está en un span gris)
                    ubi_tag = tarjeta.find("span", class_=lambda c: c and "text-gray-600" in c)
                    ubicacion = ubi_tag.text.strip() if ubi_tag else None
                    
                    # 4. Extraer Características (Están dentro de párrafos con iconos)
                    habitaciones = None
                    banos = None
                    parqueos = None
                    metros = None
                    
                    # Buscamos todos los párrafos que contienen las amenidades
                    amenidades = tarjeta.find_all("p", class_=lambda c: c and "flex" in c and "text-sm" in c)
                    for p in amenidades:
                        icono_tag = p.find("span", class_="material-symbols-outlined")
                        if icono_tag:
                            nombre_icono = icono_tag.text.strip()
                            # El valor es el texto del párrafo, quitándole el nombre del icono
                            valor = p.text.replace(nombre_icono, "").strip()
                            
                            if nombre_icono == "bed":
                                habitaciones = valor
                            elif nombre_icono == "bathtub":
                                banos = valor
                            elif nombre_icono == "directions_car":
                                parqueos = valor
                            elif nombre_icono == "square_foot":
                                metros = valor
                    
                    # Armamos el registro
                    registro = {
                        "Precio": precio,
                        "Habitaciones": habitaciones,
                        "Baños": banos,
                        "Parqueos": parqueos,
                        "Construccion (m2)": metros,
                        "Ubicacion": ubicacion,
                        "URL": url_propiedad
                    }
                    
                    dataset_citymax.append(registro)

                    # Inserción en DB
                    if conn:
                        try:
                            precio_limpio = data_cleaner.limpiar_precio_quetzales(precio)
                            area_limpia = data_cleaner.limpiar_area_metros(metros)
                            habs_limpio = data_cleaner.limpiar_entero(habitaciones)
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
                        except Exception as e_db:
                            print(f"Error al insertar en BD: {e_db}")
                    
        else:
            print(f"  -> Servidor devolvió error {response.status_code}. Saltando página.")
            
    except Exception as e:
        print(f"  -> Error de conexión en Página {pagina}: {e}")
        
    # Respiro táctico de 3 segundos entre páginas para evadir detección
    time.sleep(3) 

# --- EXPORTACIÓN A CSV ---
print("\n" + "=" * 50)
print("¡Barrido finalizado! Procesando el dataset de CityMax...")

print(f"¡Éxito total! Se procesaron y enviaron {len(dataset_citymax)} propiedades a la base de datos.")

if conn:
    conn.close()