import cloudscraper

# URL del catálogo de Inversen con los filtros aplicados
url = "https://www.inversen.com/properties/guatemala/guatemala/guatemala?ln=6451&min_bedroom=1&sort_by=price-desc"

print("Iniciando reconocimiento en el catálogo de Inversen...")

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
    nombre_archivo = "inversen_catalogo_crudo.html"
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(response.text)
        
    print(f"¡Conexión exitosa! HTML del catálogo guardado.")
    print(f"Busca el archivo '{nombre_archivo}' en tu carpeta.")
else:
    print(f"Alerta: Tuvimos un bloqueo o error. Código: {response.status_code}")