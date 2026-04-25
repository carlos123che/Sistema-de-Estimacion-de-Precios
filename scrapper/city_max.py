import cloudscraper
from bs4 import BeautifulSoup
import time
import pandas as pd

# Configuración base
BASE_URL = "https://www.citymax-gt.com"
ZONA_INICIAL = 1
ZONA_FINAL = 24

# Nuestro 'disfraz' de navegador
scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
)

dataset_citymax = []

print("Iniciando barrido táctico en CityMax (Zonas 1 a 24)...")
print("-" * 50)

# Loop para recorrer de la zona 1 a la 24
for zona in range(ZONA_INICIAL, ZONA_FINAL + 1):
    url_objetivo = f"{BASE_URL}/casas/venta/ciudad-de-guatemala/zona-{zona}"
    print(f"Escaneando Zona {zona}: {url_objetivo}")
    
    try:
        response = scraper.get(url_objetivo)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Cada casa está contenida en una etiqueta <article>
            tarjetas = soup.find_all("article")
            
            if not tarjetas:
                print(f"  -> No se encontraron propiedades listadas en la Zona {zona}.")
            else:
                print(f"  -> ¡Encontradas {len(tarjetas)} propiedades en esta zona!")
                
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
                            elif nombre_icono == "directions_car":
                                parqueos = valor
                            elif nombre_icono == "square_foot":
                                metros = valor
                    
                    # Armamos el registro
                    registro = {
                        "Zona": f"Zona {zona}",
                        "Precio": precio,
                        "Habitaciones": habitaciones,
                        "Parqueos": parqueos,
                        "Construccion (m2)": metros,
                        "Ubicacion": ubicacion,
                        "URL": url_propiedad
                    }
                    
                    dataset_citymax.append(registro)
                    
        else:
            print(f"  -> Servidor devolvió error {response.status_code}. Saltando zona.")
            
    except Exception as e:
        print(f"  -> Error de conexión en Zona {zona}: {e}")
        
    # Respiro táctico de 3 segundos entre zonas para evadir detección
    time.sleep(3) 

# --- EXPORTACIÓN A CSV ---
print("\n" + "=" * 50)
print("¡Barrido finalizado! Procesando el dataset de CityMax...")

if dataset_citymax:
    df_citymax = pd.DataFrame(dataset_citymax)
    nombre_archivo = "dataset_citymax_zonas_1_24.csv"
    df_citymax.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
    print(f"¡Éxito total! Se exportaron {len(df_citymax)} propiedades a '{nombre_archivo}'.")
else:
    print("No se logró extraer ninguna propiedad en el rango indicado.")