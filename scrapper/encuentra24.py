import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time

def scraper_encuentra24(url):
    print(f"Iniciando infiltración en: {url}")
    
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    
    response = scraper.get(url)
    
    if response.status_code != 200:
        print(f"Error {response.status_code}: Nos bloquearon o la página cayó.")
        return []

    print("HTML descargado con éxito. Analizando etiquetas...\n")
    soup = BeautifulSoup(response.text, 'html.parser')
    casas_extraidas = []

    tarjetas = soup.find_all('a', class_='item-card-link')
    
    print(f"¡Se encontraron {len(tarjetas)} propiedades en esta página!")

    for tarjeta in tarjetas:
        try:
            # 1. Extraer Título
            titulo_tag = tarjeta.find('h3', class_='card_title')
            titulo = titulo_tag.text.strip() if titulo_tag else "Sin título"

            # 2. Extraer Precio (Y limpiamos el texto)
            precio_tag = tarjeta.find('span', class_='card_price')
            precio = precio_tag.text.strip() if precio_tag else "Sin precio"

            # 3. Extraer Ubicación
            ubicacion_tag = tarjeta.find('p', class_='card_subtitle')
            ubicacion = ubicacion_tag.text.strip() if ubicacion_tag else "Sin ubicacion"

            # 4. Extraer Link de la propiedad
            link = "https://www.encuentra24.com" + tarjeta['href'] if tarjeta.has_attr('href') else ""

            # 5. Extraer Variables Físicas (Área, Habitaciones, Baños)
            specs = tarjeta.find_all('span', class_='card_spec')
            habitaciones = "0"
            banos = "0"
            area_m2 = "0"

            for spec in specs:
                texto = spec.text.lower()
                if 'recámara' in texto or 'habitación' in texto or 'cuarto' in texto:
                    habitaciones = texto.replace('recámaras', '').replace('recámara', '').strip()
                elif 'baño' in texto:
                    banos = texto.replace('baños', '').replace('baño', '').strip()
                elif 'm²' in texto or 'mts' in texto:
                    area_m2 = texto.replace('m²', '').strip()

            # Guardamos todo en nuestro diccionario 
            casas_extraidas.append({
                "Titulo": titulo,
                "Precio_Crudo": precio,
                "Ubicacion": ubicacion,
                "Habitaciones": habitaciones,
                "Banos": banos,
                "Area_m2": area_m2,
                "URL": link
            })

        except Exception as e:
            print(f"Fallo al procesar una tarjeta: {e}")
            continue

    return casas_extraidas

# ==========================================
# EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    url_objetivo = "https://www.encuentra24.com/guatemala-es/bienes-raices-venta-de-propiedades-casas"
    
    datos = scraper_encuentra24(url_objetivo)
    
    if datos:
        # Convertimos la lista de diccionarios en un DataFrame de Pandas
        df = pd.DataFrame(datos)
        
        print("\n=== MUESTRA DE LOS DATOS EXTRAÍDOS ===")
        # Imprimimos solo algunas columnas para que quepa en la consola
        print(df[['Titulo', 'Precio_Crudo', 'Habitaciones', 'Area_m2']].head(5))
        
        # Exportamos a CSV para que lo podás abrir en Excel
        nombre_archivo = "dataset_casas_encuentra24.csv"
        df.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
        print(f"\n¡Éxito total! Se guardó el archivo: {nombre_archivo}")