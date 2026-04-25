import cloudscraper

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
    with open("mapa_inmueble_crudo.html", "w", encoding="utf-8") as archivo:
        archivo.write(response.text)
        
else:
    print(f"Error: {response.status_code}")