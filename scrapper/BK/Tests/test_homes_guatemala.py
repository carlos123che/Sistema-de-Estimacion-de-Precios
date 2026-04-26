import cloudscraper

url = "https://homesguatemala.com/"

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

response = scraper.get(url)

if response.status_code == 200:
    nombre_archivo = "homes_guatemala_crudo.html"
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(response.text)
        
else:
    print(f"Código de error: {response.status_code}")