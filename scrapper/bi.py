import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import db_config
import data_cleaner

def iniciar_navegador():
    print("Iniciando navegador en modo sigiloso...")
    options = uc.ChromeOptions()
    options.add_argument('--start-maximized')
    # Opciones adicionales para evitar detección
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Especificamos la versión principal de Chrome detectada (147)
    # Esto soluciona el error de "ChromeDriver only supports Chrome version 148"
    version_chrome = 147 
    
    try:
        driver = uc.Chrome(options=options, version_main=version_chrome)
        return driver
    except Exception as e:
        print(f"Error al iniciar undetected-chromedriver (v{version_chrome}): {e}")
        print("Intentando detección automática o configuración alternativa...")
        try:
            # Reintentar sin especificar versión (detección automática)
            driver = uc.Chrome(options=options)
            return driver
        except Exception as e2:
            print(f"Error crítico al usar undetected-chromedriver: {e2}")
            print("Cambiando a Selenium estándar con tácticas de sigilo manuales...")
            
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            # Configuración para intentar pasar desapercibido con Selenium estándar
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            
            # Script para ocultar que es un bot (webdriver = undefined)
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            })
            
            return driver

def delay_aleatorio(min_sec=2, max_sec=5):
    time.sleep(random.uniform(min_sec, max_sec))

def extraer_urls_propiedades(driver, url_principal):
    print(f"Abriendo catálogo principal: {url_principal}")
    driver.get(url_principal)
    urls_propiedades = []
    
    ultima_cantidad = 0
    intentos_sin_cambio = 0

    while True:
        try:
            # Esperar a que las tarjetas carguen
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#listings__container a"))
            )
            delay_aleatorio(2, 4)
            
            tarjetas = driver.find_elements(By.CSS_SELECTOR, "#listings__container a")
            for tarjeta in tarjetas:
                link = tarjeta.get_attribute('href')
                if link and link not in urls_propiedades:
                    urls_propiedades.append(link)
            
            nueva_cantidad = len(urls_propiedades)
            print(f"Recolectadas {nueva_cantidad} URLs hasta ahora...")

            # Verificar si realmente estamos avanzando
            if nueva_cantidad == ultima_cantidad:
                intentos_sin_cambio += 1
                if intentos_sin_cambio >= 3:
                    print("No se detectaron nuevas URLs en 3 intentos. Finalizando recolección.")
                    break
            else:
                intentos_sin_cambio = 0
                ultima_cantidad = nueva_cantidad
            
            # Intentar encontrar el botón de siguiente
            try:
                boton_siguiente = driver.find_element(By.CSS_SELECTOR, "a.next, .pagination a[rel='next'], a.pagination-next")
                
                if "disabled" in boton_siguiente.get_attribute("class") or boton_siguiente.get_attribute("disabled"):
                    print("Llegamos a la última página.")
                    break
                    
                driver.execute_script("arguments[0].scrollIntoView();", boton_siguiente)
                delay_aleatorio(1, 2)
                driver.execute_script("arguments[0].click();", boton_siguiente)
                
                print("Cargando siguiente página...")
                delay_aleatorio(4, 6) 
                
            except Exception:
                print("No se encontró botón 'Siguiente' o llegamos al final.")
                break
        except Exception as e:
            print(f"Error durante la recolección: {e}")
            break
            
    return urls_propiedades

def extraer_detalle_propiedad(driver, url):
    print(f"Explorando propiedad: {url}")
    try:
        driver.get(url)
        delay_aleatorio(2, 4)
        
        datos = {'URL': url}
        
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1")) 
        )
        
        # Extracción de Título
        try:
            datos['Título'] = driver.find_element(By.TAG_NAME, "h1").text
        except:
            datos['Título'] = 'N/A'
            
        # Extracción de Precio
        try:
            precio_el = driver.find_element(By.CSS_SELECTOR, ".cuota-total-vivienda, .info-cuotas-item-1, .price-amount")
            datos['Precio'] = precio_el.text
        except:
            try:
                precio_total_el = driver.find_element(By.XPATH, "//*[contains(text(), 'Precio Total:')]")
                datos['Precio'] = precio_total_el.text.replace("Precio Total:", "").strip()
            except:
                datos['Precio'] = 'N/A'
            
        # Extracción de Detalles Técnicos por etiquetas conocidas
        try:
            items = driver.find_elements(By.CLASS_NAME, "vivienda_esp_generales_items")
            for item in items:
                try:
                    strong_tag = item.find_element(By.TAG_NAME, "strong")
                    label = strong_tag.text.lower()
                    valor = item.text.replace(strong_tag.text, "").strip()
                    
                    if "metraje" in label: datos['Área'] = valor
                    elif "dormitorios" in label: datos['Habitaciones'] = valor
                    elif "baños" in label: datos['Baños'] = valor
                    elif "parqueos" in label: datos['Parqueos'] = valor
                except:
                    continue
        except:
            pass

        # Respaldo si faltan datos usando selectores genéricos
        if len(datos) < 5:
            try:
                especificaciones = driver.find_elements(By.CSS_SELECTOR, "div[class*='spec'], div[class*='info'], .specifications__item")
                for item in especificaciones:
                    texto = item.text.lower()
                    if ("metraje" in texto or "mts2" in texto) and 'Área' not in datos:
                        datos['Área'] = item.text
                    elif "dormitorio" in texto and 'Habitaciones' not in datos:
                        datos['Habitaciones'] = item.text
                    elif "baño" in texto and 'Baños' not in datos:
                        datos['Baños'] = item.text
                    elif "parqueo" in texto and 'Parqueos' not in datos:
                        datos['Parqueos'] = item.text
            except:
                pass

        print(f"  [>] Datos extraídos: Precio: {datos.get('Precio')}, Área: {datos.get('Área')}, Hab: {datos.get('Habitaciones')}")
        return datos
        
    except Exception as e:
        print(f"Error extrayendo datos de {url}: {e}")
        return {'URL': url, 'Precio': 'N/A', 'Título': 'N/A'}

if __name__ == "__main__":
    url_base = "https://blog.corporacionbi.com/bi-vienda-en-linea-banco-industrial/conoce-tus-opciones"
    
    driver = iniciar_navegador()
    conn = db_config.get_connection()
    
    if conn:
        id_fuente = db_config.get_or_create_fuente(conn, "Banco Industrial", url_base)
    else:
        print("Advertencia: No se pudo conectar a la base de datos.")
    
    try:
        lista_urls = extraer_urls_propiedades(driver, url_base)
        print(f"Total de propiedades a procesar: {len(lista_urls)}")
        
        total = len(lista_urls)
        for i, url_propiedad in enumerate(lista_urls):
            print(f"[{i+1}/{total}] Procesando: {url_propiedad}")
            info = extraer_detalle_propiedad(driver, url_propiedad)
            
            if conn:
                try:
                    precio_limpio = data_cleaner.limpiar_precio_quetzales(info.get('Precio'))
                    area_limpia = data_cleaner.limpiar_area_metros(info.get('Área'))
                    habs_limpio = data_cleaner.limpiar_entero(info.get('Habitaciones'))
                    banos_limpio = data_cleaner.limpiar_decimal(info.get('Baños'))
                    parqueos_limpio = data_cleaner.limpiar_entero(info.get('Parqueos'))
                    
                    titulo = info.get('Título', '')
                    nombre_zona = data_cleaner.extraer_zona(titulo)
                    id_zona_db = db_config.get_or_create_zona(conn, nombre_zona)
                    
                    tipo_id = db_config.get_or_create_tipo_inmueble(conn, "Inmueble")
                    if "apartamento" in titulo.lower(): 
                        tipo_id = db_config.get_or_create_tipo_inmueble(conn, "Apartamento")
                    elif "casa" in titulo.lower() or "residencia" in titulo.lower(): 
                        tipo_id = db_config.get_or_create_tipo_inmueble(conn, "Casa")
                        
                    datos_db = {
                        'id_fuente': id_fuente, 
                        'id_zona': id_zona_db, 
                        'id_tipo_inmueble': tipo_id,
                        'precio_quetzales': precio_limpio, 
                        'area_metros': area_limpia,
                        'habitaciones': habs_limpio, 
                        'baños': banos_limpio, 
                        'parqueos': parqueos_limpio,
                        'url': url_propiedad
                    }
                    db_config.insert_inmueble(conn, datos_db)
                except Exception as e_db:
                    print(f" Error DB: {e_db}")
            
            # Delay aleatorio entre propiedades para simular comportamiento humano
            delay_aleatorio(1, 3)
            
    finally:
        if 'driver' in locals() and driver:
            driver.quit()
        if 'conn' in locals() and conn:
            conn.close()