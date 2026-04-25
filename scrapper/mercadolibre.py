from playwright.sync_api import sync_playwright
import time
import re

def extraer_urls_live(page):
    url_objetivo = "https://inmuebles.mercadolibre.com.gt/casas/venta/"
    print(f"Navegando al índice: {url_objetivo}")
    
    page.goto(url_objetivo, wait_until="domcontentloaded")
    time.sleep(4) # Espera táctica
    
    # Inyección JS para robar URLs
    todos_los_hrefs = page.evaluate("""
        () => {
            const enlaces = Array.from(document.querySelectorAll('a'));
            return enlaces.map(a => a.href);
        }
    """)
    
    urls_limpias = set()
    for href in todos_los_hrefs:
        if href and "MGT-" in href:
            url_base = href.split('#')[0].split('?')[0]
            if "mercadolibre.com.gt/MGT-" in url_base:
                urls_limpias.add(url_base)
                
    return list(urls_limpias)

def extraer_detalles_propiedad(page, url):
    print(f"  -> Analizando: {url}")
    try:
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(3) # Pausa para no saturar el servidor y simular lectura humana
        
        # Extraemos los datos crudos usando JS
        datos_crudos = page.evaluate("""
            () => {
                const safeText = (selector) => {
                    const el = document.querySelector(selector);
                    return el ? el.innerText.replace(/\\n/g, ' ').trim() : 'N/A';
                };

                // Título y Precio (selectores estándar de Meli)
                const titulo = safeText('h1.ui-pdp-title');
                const precio = safeText('.ui-pdp-price__second-line .andes-money-amount__fraction');
                
                // Ubicación (Meli usa varias clases, tomamos el contenedor principal de ubicación)
                const ubicacion = safeText('#location .ui-pdp-media__title, .ui-seller-info .ui-pdp-media__title, .ui-vip-location__title');

                // Agrupamos todo el texto de las características (iconos rápidos y tabla detallada)
                const specsCards = Array.from(document.querySelectorAll('.ui-pdp-highlighted-specs-res__icon-label, .ui-pdp-specs__table tr, .ui-vpp-highlighted-specs__item')).map(el => el.innerText);
                
                return {
                    titulo: titulo,
                    precio: precio,
                    ubicacion: ubicacion,
                    texto_specs: specsCards.join(" | ") // Unimos todo para pasarlo a Python
                };
            }
        """)

        texto_unido = datos_crudos['texto_specs']

        # --- FASE DE LIMPIEZA CON REGEX ---
        # Buscamos los patrones exactos que me mostraste en las imágenes
        
        m_cuadros = re.search(r'(\d+)\s*m²\s*totales', texto_unido, re.IGNORECASE)
        cuadros = m_cuadros.group(1) if m_cuadros else "N/A"

        m_dormitorios = re.search(r'(\d+)\s*dorm', texto_unido, re.IGNORECASE)
        dormitorios = m_dormitorios.group(1) if m_dormitorios else "0"

        m_banos = re.search(r'(\d+)\s*baño', texto_unido, re.IGNORECASE)
        banos = m_banos.group(1) if m_banos else "0"

        # Para el garaje, puede venir como "Garajes: 1" en la tabla, o "1 parqueo" en highlights
        m_garajes = re.search(r'Garajes\s*:\s*(\d+)|(\d+)\s*estacionamiento|(\d+)\s*parqueo', texto_unido, re.IGNORECASE)
        garaje = next((g for g in m_garajes.groups() if g is not None), "0") if m_garajes else "0"

        # Empaquetamos en un diccionario limpio
        return {
            "URL": url,
            "Titulo": datos_crudos['titulo'],
            "Precio_Q": datos_crudos['precio'],
            "Ubicacion": datos_crudos['ubicacion'],
            "Metros_Cuadrados": cuadros,
            "Habitaciones": dormitorios,
            "Banos": banos,
            "Garaje": garaje
        }

    except Exception as e:
        print(f"  -> Error al extraer detalles: {e}")
        return None

if __name__ == "__main__":
    with sync_playwright() as p:
        print("Iniciando motor Playwright...")
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        try:
            urls = extraer_urls_live(page)
            print(f"\n¡Se encontraron {len(urls)} propiedades! Iniciando extracción a detalle...\n")
            
            datos_inmobiliarios = []
            
            # Limitamos a las primeras 3 para hacer la prueba inicial
            for url in urls[:3]: 
                detalles = extraer_detalles_propiedad(page, url)
                if detalles:
                    datos_inmobiliarios.append(detalles)
                    
                    # Imprimir el resultado en consola para validación
                    print("  [✓] Datos extraídos:")
                    for key, value in detalles.items():
                        if key != "URL":
                            print(f"      - {key}: {value}")
                    print("-" * 40)
            
            # Aquí tienes tu lista de diccionarios lista para convertirse en un DataFrame
            import pandas as pd
            df = pd.DataFrame(datos_inmobiliarios)
            print(df)
            df.to_csv("mercadolibre_casas.csv", index=False)
            
        except Exception as e:
            print(f"Error general: {e}")
        finally:
            browser.close()