import requests

# Encabezados para evitar bloqueos básicos
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

url_prueba = "https://www.encuentra24.com/guatemala-es/bienes-raices-venta-de-propiedades-casas"

print(f"Haciendo petición a: {url_prueba}")
response = requests.get(url_prueba, headers=HEADERS)

print(f"Código de estado: {response.status_code}")
print(response)

if response.status_code == 200:
    # Guardar HTML crudo en un archivo local
    nombre_archivo = "debug_mapainmueble.html"
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(response.text)
        
    print(f"\n¡El HTML completo se guardó en tu carpeta local como '{nombre_archivo}'.")
else:
    print("El servidor nos bloqueó o la página no existe.")