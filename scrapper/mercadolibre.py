import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import random
import db_config
import data_cleaner

def extraer_urls_live(driver):
    urls_indices = [
        "https://inmuebles.mercadolibre.com.gt/casas/venta/",
        "https://inmuebles.mercadolibre.com.gt/casas/venta/_Desde_51_NoIndex_True",
        "https://inmuebles.mercadolibre.com.gt/casas/venta/_Desde_101_NoIndex_True"
    ]
    
    urls_limpias = set()
    
    for url_objetivo in urls_indices:
        print(f"Navegando al índice: {url_objetivo}")
        try:
            driver.get(url_objetivo)
            time.sleep(random.uniform(5, 8)) # Espera aleatoria para cargar
            
            # Buscamos los enlaces de propiedades
            enlaces = driver.find_elements(By.CSS_SELECTOR, "a[href*='/MGT-'], .ui-search-item__group__element a, .ui-search-link")
            
            contador_antes = len(urls_limpias)
            for a in enlaces:
                href = a.get_attribute('href')
                if href and "MGT-" in href:
                    url_base = href.split('#')[0].split('?')[0]
                    if "mercadolibre.com.gt/MGT-" in url_base:
                        urls_limpias.add(url_base)
            
            print(f"  -> Encontradas {len(urls_limpias) - contador_antes} nuevas URLs en esta página.")
            
            # Si no encontró nada, pausar para intervención humana
            if len(urls_limpias) == 0:
                print("[!] No se detectaron URLs. Si ves un captcha o login en el navegador, resuélvelo manualmente.")
                print("[!] Presiona ENTER en esta consola cuando el listado de casas sea visible...")
                input()
                # Re-intentar extraer de la página actual
                enlaces = driver.find_elements(By.CSS_SELECTOR, "a[href*='/MGT-'], .ui-search-item__group__element a, .ui-search-link")
                for a in enlaces:
                    href = a.get_attribute('href')
                    if href and "MGT-" in href:
                        url_base = href.split('#')[0].split('?')[0]
                        if "mercadolibre.com.gt/MGT-" in url_base:
                            urls_limpias.add(url_base)

        except Exception as e:
            print(f"Error accediendo a {url_objetivo}: {e}")
                
    return list(urls_limpias)

def extraer_detalles_propiedad(driver, url):
    print(f"  -> Analizando: {url}")
    try:
        driver.get(url)
        time.sleep(random.uniform(4, 7))
        
        # Extraemos datos básicos usando selectores de Selenium
        try:
            titulo = driver.find_element(By.CSS_SELECTOR, "h1.ui-pdp-title").text
        except:
            titulo = "N/A"
            
        try:
            precio = driver.find_element(By.CSS_SELECTOR, ".ui-pdp-price__second-line .andes-money-amount__fraction").text
        except:
            precio = "N/A"
            
        try:
            ubicacion = driver.find_element(By.CSS_SELECTOR, "#location .ui-pdp-media__title, .ui-seller-info .ui-pdp-media__title, .ui-vip-location__title").text
        except:
            ubicacion = "N/A"

        # Características (Metros, Dormitorios, etc)
        specs_elements = driver.find_elements(By.CSS_SELECTOR, ".ui-pdp-highlighted-specs-res__icon-label, .ui-pdp-specs__table tr, .ui-vpp-highlighted-specs__item")
        texto_unido = " | ".join([el.text for el in specs_elements])

        # --- LIMPIEZA CON REGEX ---
        m_cuadros = re.search(r'(\d+)\s*m²\s*totales', texto_unido, re.IGNORECASE)
        cuadros = m_cuadros.group(1) if m_cuadros else "N/A"

        m_dormitorios = re.search(r'(\d+)\s*dorm', texto_unido, re.IGNORECASE)
        dormitorios = m_dormitorios.group(1) if m_dormitorios else "0"

        m_banos = re.search(r'(\d+)\s*baño', texto_unido, re.IGNORECASE)
        banos = m_banos.group(1) if m_banos else "0"

        m_garajes = re.search(r'Garajes\s*:\s*(\d+)|(\d+)\s*estacionamiento|(\d+)\s*parqueo', texto_unido, re.IGNORECASE)
        garaje = next((g for g in m_garajes.groups() if g is not None), "0") if m_garajes else "0"

        return {
            "URL": url,
            "Titulo": titulo,
            "Precio_Q": precio,
            "Ubicacion": ubicacion,
            "Metros_Cuadrados": cuadros,
            "Habitaciones": dormitorios,
            "Banos": banos,
            "Garaje": garaje
        }

    except Exception as e:
        print(f"  -> Error al extraer detalles: {e}")
        return None

if __name__ == "__main__":
    print("Iniciando Navegador Indetectable (Undetected Chromedriver)...")
    
    # Configuración de Undetected Chromedriver
    options = uc.ChromeOptions()
    # Si quieres usar tu perfil real, descomenta la línea de abajo y ajusta la ruta
    # options.add_argument(f'--user-data-dir={os.path.expanduser("~")}\\AppData\\Local\\Google\\Chrome\\User Data')
    
    # Forzamos la versión 147 para que coincida con tu navegador
    try:
        driver = uc.Chrome(options=options, version_main=147)
    except Exception as e:
        print(f"Reintentando conexión automática del driver...")
        driver = uc.Chrome(options=options)

    try:
        urls = extraer_urls_live(driver)
        
        if not urls:
            print("[!] No se encontraron propiedades. Abortando.")
            driver.quit()
            exit()
            
        print(f"\n¡Se encontraron {len(urls)} propiedades! Iniciando extracción...\n")
        
        datos_inmobiliarios = []
        conn = db_config.get_connection()
        
        if conn:
            id_fuente = db_config.get_or_create_fuente(conn, "MercadoLibre", "https://www.mercadolibre.com.gt")
            id_tipo_inmueble = db_config.get_or_create_tipo_inmueble(conn, "Casa")
        
        for url in urls:
            detalles = extraer_detalles_propiedad(driver, url)
            if detalles:
                datos_inmobiliarios.append(detalles)
                
                if conn:
                    try:
                        precio_limpio = data_cleaner.limpiar_precio_quetzales(detalles['Precio_Q'])
                        area_limpia = data_cleaner.limpiar_area_metros(detalles['Metros_Cuadrados'])
                        habs_limpio = data_cleaner.limpiar_entero(detalles['Habitaciones'])
                        banos_limpio = data_cleaner.limpiar_decimal(detalles['Banos'])
                        parqueos_limpio = data_cleaner.limpiar_entero(detalles['Garaje'])
                        
                        nombre_zona = data_cleaner.extraer_zona(detalles['Ubicacion'])
                        id_zona_db = db_config.get_or_create_zona(conn, nombre_zona)
                        
                        datos_db = {
                            'id_fuente': id_fuente,
                            'id_zona': id_zona_db,
                            'id_tipo_inmueble': id_tipo_inmueble,
                            'precio_quetzales': precio_limpio,
                            'area_metros': area_limpia,
                            'habitaciones': habs_limpio,
                            'baños': banos_limpio,
                            'parqueos': parqueos_limpio,
                            'url': url
                        }
                        db_config.insert_inmueble(conn, datos_db)
                        print(f"  [✓] Insertado en BD: {detalles['Titulo'][:50]}...")
                    except Exception as e_db:
                        print(f"Error al insertar en BD: {e_db}")
            
            # Pausa humana
            time.sleep(random.uniform(5, 12))
            
    except Exception as e:
        print(f"Error general: {e}")
    finally:
        driver.quit()
        if 'conn' in locals() and conn:
            conn.close()