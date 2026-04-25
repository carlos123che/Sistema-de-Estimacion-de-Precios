import cloudscraper

# URL de búsqueda de casas en venta en Guatemala
url = "https://inmuebles.mercadolibre.com.gt/casas/venta/"

print("Iniciando escaneo en Mercado Libre Inmuebles...")

# Configuramos el scraper con un delay y especificaciones de navegador
scraper = cloudscraper.create_scraper(
    delay=10, 
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True 
    }
)

# Añadimos un User-Agent realista para evitar bloqueos inmediatos
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9',
    'Referer': 'https://www.google.com/'
}

try:
    response = scraper.get(url, headers=headers)

    if response.status_code == 200:
        nombre_archivo = "mercadolibre_casas.html"
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            archivo.write(response.text)
        
        print(f"Éxito: Datos de Mercado Libre guardados en {nombre_archivo}")
        print(f"Tamaño del archivo: {len(response.text) / 1024:.2f} KB")
    else:
        print(f"Error de acceso: Código {response.status_code}")
        if response.status_code == 403:
            print("Aviso: Mercado Libre detectó el script. Podrías necesitar un proxy o resolver un captcha.")

except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")