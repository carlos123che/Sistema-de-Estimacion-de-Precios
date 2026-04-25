from bs4 import BeautifulSoup
import json
import pandas as pd

# Abrimos el archivo que guardaste en el paso anterior
# Asegúrate de que el nombre coincida con el archivo en tu computadora
with open("inversen_catalogo_crudo.html", "r", encoding="utf-8") as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, 'html.parser')

# Buscamos todas las tarjetas de propiedades
propiedades = soup.find_all('div', class_='property-listing')

datos_extraidos = []

print(f"Se encontraron {len(propiedades)} propiedades en esta página.\n")

for prop in propiedades:
    # 1. Aprovechamos el JSON oculto en el atributo data-popover-data
    popover_str = prop.get('data-popover-data')
    
    if popover_str:
        try:
            info = json.loads(popover_str)
            
            # 2. Extraemos los valores del JSON
            titulo = info.get('title', 'N/A')
            precio = info.get('price', 'N/A')
            habitaciones = info.get('bedrooms', 'N/A')
            banos = info.get('bathrooms', 'N/A')
            tamano_m2 = info.get('size', 'N/A')
            ubicacion = info.get('location', 'N/A')
            
            # 3. Armamos la URL completa
            url_relativa = info.get('url', '')
            url_completa = f"https://www.inversen.com{url_relativa}" if url_relativa else 'N/A'
            
            # 4. Extraemos latitud y longitud (fuera del JSON, en la etiqueta div)
            lat = prop.get('data-lat', 'N/A')
            lon = prop.get('data-long', 'N/A')
            
            # Guardamos en nuestro diccionario
            datos_extraidos.append({
                'Título': titulo,
                'Precio': precio,
                'Habitaciones': habitaciones,
                'Baños': banos,
                'Tamaño': tamano_m2,
                'Ubicación': ubicacion,
                'Latitud': lat,
                'Longitud': lon,
                'URL': url_completa
            })
            
        except json.JSONDecodeError:
            print("Error decodificando JSON en una de las propiedades.")

# Convertimos la lista de diccionarios a un DataFrame de Pandas
df_inversen = pd.DataFrame(datos_extraidos)

# Mostramos las primeras 5 filas para verificar
print(df_inversen[['Precio', 'Habitaciones', 'Baños', 'Tamaño', 'Latitud']].head())

# Opcional: Exportar a CSV
df_inversen.to_csv('datos_inversen.csv', index=False, encoding='utf-8')