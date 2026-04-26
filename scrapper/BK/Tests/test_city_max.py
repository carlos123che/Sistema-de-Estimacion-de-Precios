import cloudscraper

# URL del catálogo de CityMax
url = "https://www.citymax-gt.com/casas/venta/guatemala"

print("Iniciando reconocimiento en el catálogo de CityMax...")

# Nuestro 'disfraz' de navegador
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

response = scraper.get(url)

if response.status_code == 200:
    # Guardamos el HTML crudo
    nombre_archivo = "citymax_catalogo_crudo.html"
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(response.text)
        
    print(f"¡Conexión exitosa! HTML del catálogo guardado.")
    print(f"Busca el archivo '{nombre_archivo}' en tu carpeta.")
else:
    print(f"Alerta: Tuvimos un bloqueo o error. Código: {response.status_code}")