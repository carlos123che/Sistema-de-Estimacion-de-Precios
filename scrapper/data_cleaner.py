import re
import os
from dotenv import load_dotenv

load_dotenv()

# Tasa de cambio configurada en el archivo .env, default 7.8 si no existe
TASA_CAMBIO = float(os.getenv("TASA_CAMBIO_USD_A_Q", 7.80))

def limpiar_precio_quetzales(precio_str):
    """
    Recibe un string de precio (ej. 'Q 4,000,000', '$ 275,000', 'USD 1,100,000')
    y retorna un float en Quetzales. Si no puede, retorna None.
    """
    if not precio_str or precio_str == 'N/A' or not isinstance(precio_str, str):
        return None
    
    precio_str_upper = precio_str.upper()
    es_usd = '$' in precio_str_upper or 'USD' in precio_str_upper
    
    # Extraer solo números y puntos decimales
    numeros = re.findall(r'[0-9\.]+', precio_str.replace(',', ''))
    if not numeros:
        return None
        
    try:
        valor = float(numeros[0])
        if es_usd:
            valor = valor * TASA_CAMBIO
        return round(valor, 2)
    except ValueError:
        return None

def limpiar_area_metros(area_str):
    """
    Recibe un string de área (ej. '367m2', '204.82m2', '1,200m2', '2,329.00 mt2')
    y retorna un float en metros cuadrados.
    """
    if not area_str or pd.isna(area_str) if 'pd' in globals() else area_str == 'N/A' or not isinstance(area_str, str):
        return None
        
    # Remover comas
    area_limpia = area_str.replace(',', '')
    
    # Extraer números
    numeros = re.findall(r'[0-9\.]+', area_limpia)
    if not numeros:
        return None
        
    try:
        valor = float(numeros[0])
        # Si la unidad son varas cuadradas (v2), se convierte a m2
        # 1 vara cuadrada = 0.698896 metros cuadrados aprox.
        if 'v' in area_str.lower() and 'm' not in area_str.lower():
            valor = valor * 0.698896
        return round(valor, 2)
    except ValueError:
        return None

def limpiar_entero(entero_str):
    """
    Limpia texto de habitaciones o parqueos (ej. '4 habitaciones', '2') y devuelve int.
    """
    if not entero_str or entero_str == 'N/A':
        return None
    
    if isinstance(entero_str, (int, float)):
        return int(entero_str)
        
    numeros = re.findall(r'\d+', str(entero_str))
    if numeros:
        return int(numeros[0])
    return None

def limpiar_decimal(decimal_str):
    """
    Para baños, que a veces son 2.5
    """
    if not decimal_str or decimal_str == 'N/A':
        return None
        
    if isinstance(decimal_str, (int, float)):
        return float(decimal_str)
        
    numeros = re.findall(r'[0-9\.]+', str(decimal_str))
    if numeros:
        return float(numeros[0])
    return None

def extraer_zona(ubicacion_str):
    """
    Busca patrones de 'Zona X' o 'Z X' o 'Z. X' en el texto.
    Retorna el nombre de la zona, ej. 'Zona 10'. Si no encuentra, puede retornar 'Otra' o 'Ciudad de Guatemala' etc.
    """
    if not ubicacion_str or not isinstance(ubicacion_str, str):
        return "Otra"
        
    match = re.search(r'zona\s*(\d+)', ubicacion_str, re.IGNORECASE)
    if match:
        return f"Zona {match.group(1)}"
        
    match_z = re.search(r'z\.?\s*(\d+)', ubicacion_str, re.IGNORECASE)
    if match_z:
        return f"Zona {match_z.group(1)}"
        
    # Si no es zona específica pero hay una palabra clave
    if 'carretera a el salvador' in ubicacion_str.lower() or 'caes' in ubicacion_str.lower():
        return "Carretera a El Salvador"
    if 'san josé pinula' in ubicacion_str.lower() or 'san jose pinula' in ubicacion_str.lower():
        return "San José Pinula"
    if 'fraijanes' in ubicacion_str.lower():
        return "Fraijanes"
    if 'mixco' in ubicacion_str.lower():
        return "Mixco"
    if 'villa nueva' in ubicacion_str.lower():
        return "Villa Nueva"
    
    return "Otra"
