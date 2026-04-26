import cloudscraper

# URL del sitio de opciones de vivienda de Banco Industrial
url = "https://blog.corporacionbi.com/bi-vienda-en-linea-banco-industrial/conoce-tus-opciones"

print("Iniciando reconocimiento en el portal de Banco Industrial...")

# Mantenemos nuestro 'disfraz' de navegador
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
    nombre_archivo = "bi_catalogo_crudo.html"
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(response.text)
        
    print(f"¡Conexión exitosa! HTML del catálogo guardado.")
    print(f"Busca el archivo '{nombre_archivo}' en tu carpeta.")
else:
    print(f"Alerta: Tuvimos un bloqueo o error. Código: {response.status_code}")