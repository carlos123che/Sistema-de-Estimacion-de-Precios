import cloudscraper
from bs4 import BeautifulSoup
import time
import re
import pandas as pd 

# Configuración inicial
URL_PRINCIPAL = "https://fha.gob.gt/casas/usadas"
BASE_URL = "https://fha.gob.gt"

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
)

def extraer_caracteristica(soup_obj, etiqueta):
    nodo_etiqueta = soup_obj.find(lambda tag: tag.name == "p" and etiqueta in tag.text)
    if nodo_etiqueta:
        nodo_valor = nodo_etiqueta.find_next_sibling("p")
        if nodo_valor:
            return " ".join(nodo_valor.text.split())
    return None

print(f"Mapeo del catálogo en {URL_PRINCIPAL}...")
response = scraper.get(URL_PRINCIPAL)

if response.status_code == 200:
    soup_index = BeautifulSoup(response.text, "html.parser")
    
    enlaces = soup_index.find_all("a", href=re.compile(r"/casas/usadas/\d+"))
    urls_detalles = list(set([BASE_URL + link['href'] for link in enlaces]))
    
    print(f"- {len(urls_detalles)}\n")

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
                    "Precio (Q)": extraer_caracteristica(soup_casa, "Precio:"),
                    "Enganche (Q)": extraer_caracteristica(soup_casa, "Enganche desde:"),
                    "Cuota (Q)": extraer_caracteristica(soup_casa, "Cuota desde:"),
                    "Terreno": extraer_caracteristica(soup_casa, "Terreno:"),
                    "Construcción": extraer_caracteristica(soup_casa, "Construcción:"),
                    "Parqueos": extraer_caracteristica(soup_casa, "Parqueos:"),
                    "Ambientes": extraer_caracteristica(soup_casa, "Ambientes:"),
                    "Departamento": extraer_caracteristica(soup_casa, "Departamento:"),
                    "Municipio": extraer_caracteristica(soup_casa, "Municipio:"),
                    "Ubicación": extraer_caracteristica(soup_casa, "Ubicación:")
                }
                
                dataset_casas.append(registro)
            else:
                print(f"  -> Código de error {resp_casa.status_code} al acceder.")
                
        except Exception as e:
            print(f"  -> Ocurrió un error con esta URL: {e}")
            
        time.sleep(2) 
        
    print("\nExtracción finalizada")
    
    df_casas = pd.DataFrame(dataset_casas)
    
    nombre_archivo = "dataset_fha_casas_usadas.csv"
    df_casas.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
    
    print(f"Dataset guardado como '{nombre_archivo}'.")
    print(f"Total de registros exportados: {len(df_casas)}")

else:
    print(f"Error al acceder al índice: {response.status_code}")