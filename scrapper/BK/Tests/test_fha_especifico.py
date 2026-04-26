import cloudscraper

# URL directa al detalle de una propiedad del FHA
url = "https://fha.gob.gt/casas/usadas/2004494"

print("Iniciando escaneo táctico en el portal del FHA...")

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

response = scraper.get(url)

if response.status_code == 200:
    nombre_archivo = "fha_detalle_crudo.html"
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(response.text)
        
    print(f"Conexión exitosa. HTML guardado.")
else:
    print(f"Código de error: {response.status_code}")