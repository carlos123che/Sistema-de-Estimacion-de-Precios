from bs4 import BeautifulSoup
import pandas as pd

print("Analizando el HTML renderizado...")
with open("homes_guatemala_renderizado.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

lista_propiedades = []

tarjetas = soup.find_all("div", class_="p-6")

for tarjeta in tarjetas:

    titulo_tag = tarjeta.find("p", class_=lambda x: x and "text-xl" in x)

    ubicacion_tag = tarjeta.find("p", class_=lambda x: x and "text-sm" in x)
 
    precio_tag = tarjeta.find("p", class_=lambda x: x and "text-2xl" in x)
    
    if titulo_tag and precio_tag:
        titulo = titulo_tag.text.strip()
        ubicacion = ubicacion_tag.text.strip() if ubicacion_tag else "Sin ubicación"
        precio = precio_tag.text.strip()
        
        precio_limpio = precio.replace('$', '').replace(',', '').strip()
        
        lista_propiedades.append({
            "Titulo": titulo,
            "Ubicacion": ubicacion,
            "Precio_USD": precio_limpio
        })

if lista_propiedades:
    df = pd.DataFrame(lista_propiedades)
    print("\nMuestra de los datos extraídos")
    print(df.head())
    
    # Guardamos en CSV
    df.to_csv("dataset_homes_guatemala.csv", index=False, encoding="utf-8")
    print(f"\n¡Se guardaron {len(df)} propiedades en 'dataset_homes_guatemala.csv'.")
else:
    print("no se encontraron propiedades. Revisa la estructura del HTML.")