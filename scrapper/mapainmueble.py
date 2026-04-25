import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd

url = "https://mapainmueble.com/casas-en-venta-guatemala/"


scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

response = scraper.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    datos_casas = []
    
    tarjetas = soup.find_all('div', class_='listing_wrapper')
    
    print(f"Se encontraron {len(tarjetas)} propiedades en la página.\n")
    
    for tarjeta in tarjetas:
        # TÍTULO y URL
        titulo = tarjeta.get('data-modal-title', 'N/A')
        link = tarjeta.get('data-modal-link', 'N/A')
        
        # PRECIO
        precio_tag = tarjeta.find('div', class_='listing_unit_price_wrapper')
        precio = precio_tag.text.replace('\n', '').strip() if precio_tag else 'N/A'
        
        # UBICACIÓN
        loc_tag = tarjeta.find('div', class_='property_location_image')
        ubicacion = " ".join([a.text.strip() for a in loc_tag.find_all('a')]) if loc_tag else 'N/A'
        
        # HABITACIONES
        room_tag = tarjeta.find('span', class_='inforoom')
        habitaciones = room_tag.text.strip() if room_tag else 'N/A'
        
        # BAÑOS
        bath_tag = tarjeta.find('span', class_='infobath')
        banos = bath_tag.text.strip() if bath_tag else 'N/A'
        
        # ÁREA
        size_tag = tarjeta.find('span', class_='infosize')
        area = size_tag.text.strip() if size_tag else 'N/A'
        
        datos_casas.append({
            'Titulo': titulo,
            'Precio_Crudo': precio,
            'Ubicacion': ubicacion,
            'Habitaciones': habitaciones,
            'Banos': banos,
            'Area_m2': area,
            'URL': link
        })

    # PASO 2: Convertir a DataFrame 
    df = pd.DataFrame(datos_casas)
    print(df.head())
    
    # PASO 3: Guardar el CSV
    df.to_csv('mapainmueble_data.csv', index=False, encoding='utf-8')
    print("\n Archivo 'mapainmueble_data.csv' generado con éxito. ")

else:
    print(f"Error al conectar. Código: {response.status_code}")