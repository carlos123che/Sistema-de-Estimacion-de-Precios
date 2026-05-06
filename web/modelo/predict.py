import joblib
import pandas as pd
import sys

def predict_price(zona, tipo_inmueble, area_metros, habitaciones, baños, parqueos):
    """
    Carga el modelo y realiza una predicción basada en los parámetros ingresados.
    """
    try:
        # Cargar el modelo guardado
        model = joblib.load('modelo_precio_inmuebles.pkl')
        
        # Crear un DataFrame con los datos de entrada
        input_data = pd.DataFrame([{
            'zona': zona,
            'tipo_inmueble': tipo_inmueble,
            'area_metros': area_metros,
            'habitaciones': habitaciones,
            'baños': baños,
            'parqueos': parqueos
        }])
        
        # Realizar la predicción
        prediction = model.predict(input_data)[0]
        
        return prediction
    except FileNotFoundError:
        print("Error: El archivo del modelo 'modelo_precio_inmuebles.pkl' no existe. Ejecuta 'train_model.py' primero.")
        return None
    except Exception as e:
        print(f"Error durante la predicción: {e}")
        return None

if __name__ == "__main__":
    # Ejemplo de uso si se ejecuta directamente
    print("--- Estimador de Precios de Inmuebles ---")
    
    # Valores de prueba (puedes cambiarlos)
    test_zona = "Zona 10"
    test_tipo = "Apartamento"
    test_area = 120.0
    test_hab = 3
    test_baños = 2.5
    test_parq = 2
    
    print(f"Prediciendo para: {test_tipo} en {test_zona}, {test_area}m², {test_hab} habs, {test_baños} baños, {test_parq} parq.")
    
    estimacion = predict_price(test_zona, test_tipo, test_area, test_hab, test_baños, test_parq)
    
    if estimacion:
        print(f"\nPrecio estimado: Q {estimacion:,.2f}")
