from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

def iniciar_navegador():
    opciones = webdriver.ChromeOptions()
    opciones.add_argument('--start-maximized')    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opciones)
    return driver

def extraer_urls_propiedades(driver, url_principal):
    print(f"Abriendo catálogo principal: {url_principal}")
    driver.get(url_principal)
    urls_propiedades = []
    
    while True:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#listings__container a"))
        )
        time.sleep(2)
        
        tarjetas = driver.find_elements(By.CSS_SELECTOR, "#listings__container a")
        for tarjeta in tarjetas:
            link = tarjeta.get_attribute('href')
            if link and link not in urls_propiedades:
                urls_propiedades.append(link)
                
        print(f"Recolectadas {len(urls_propiedades)} URLs hasta ahora...")
        
        try:
            boton_siguiente = driver.find_element(By.XPATH, "//div[contains(@class, 'pagination')]//a[contains(text(), '»') or contains(@class, 'next')]")
            
            if "disabled" in boton_siguiente.get_attribute("class"):
                print("Llegamos a la última página.")
                break
            if "disabled" in boton_siguiente.get_attribute("class"):
                print("Llegamos a la última página.")
                break
                
            driver.execute_script("arguments[0].scrollIntoView();", boton_siguiente)
            time.sleep(1)
            boton_siguiente.click()
            
            time.sleep(3) 
            
        except Exception as e:
            print("No hay más páginas o no se encontró el botón de 'Siguiente'.")
            break
            
    return urls_propiedades

def extraer_detalle_propiedad(driver, url):
    print(f"Explorando propiedad: {url}")
    driver.get(url)
    datos = {'URL': url}
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1")) 
        )
        time.sleep(1)
        
        try:
            precio = driver.find_element(By.XPATH, "//*[contains(text(), '$') or contains(text(), 'Q ')]").text
            datos['Precio'] = precio
        except:
            datos['Precio'] = 'N/A'
            
        try:
            datos['Título'] = driver.find_element(By.TAG_NAME, "h1").text
        except:
            datos['Título'] = 'N/A'
            
        texto_pagina = driver.find_element(By.TAG_NAME, "body").text
        
        lineas = texto_pagina.split('\n')
        for i, linea in enumerate(lineas):
            linea_lower = linea.lower()
            if "dormitorio" in linea_lower:
                datos['Habitaciones'] = linea
            elif "baño" in linea_lower:
                datos['Baños'] = linea
            elif "parqueo" in linea_lower or "estacionamiento" in linea_lower or "vehículos" in linea_lower:
                datos['Parqueos'] = linea
            elif "mts2" in linea_lower or "m2" in linea_lower or "vrs2" in linea_lower or "metraje" in linea_lower:
                datos['Área'] = linea
            elif "código" in linea_lower:
                datos['Código'] = linea
                
    except Exception as e:
        print(f"Error extrayendo datos de {url}: {e}")
        
    return datos

if __name__ == "__main__":
    url_base = "https://blog.corporacionbi.com/bi-vienda-en-linea-banco-industrial/conoce-tus-opciones"
    
    driver = iniciar_navegador()
    
    try:
        lista_urls = extraer_urls_propiedades(driver, url_base)
        print(f"Total de propiedades a procesar: {len(lista_urls)}")
        
        datos_completos = []
        for url_propiedad in lista_urls:
            info_propiedad = extraer_detalle_propiedad(driver, url_propiedad)
            datos_completos.append(info_propiedad)
            
        df = pd.DataFrame(datos_completos)
        df.to_csv("datos_bi_vivienda.csv", index=False, encoding='utf-8')
        print("\n¡Misión cumplida! Datos guardados en 'datos_bi_vivienda.csv'")
        
    finally:
        driver.quit()