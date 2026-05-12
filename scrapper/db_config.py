import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "bienes_raices_db")
DB_PORT = os.getenv("DB_PORT", "5432")

def get_connection():
    """Establece y retorna una conexión a la base de datos PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def get_or_create_fuente(conn, nombre_fuente, url_fuente):
    """Busca o crea una fuente en la DB y retorna su ID."""
    with conn.cursor() as cur:
        cur.execute("SELECT id_fuente FROM Fuente WHERE nombre_fuente = %s;", (nombre_fuente,))
        res = cur.fetchone()
        if res:
            return res[0]
        else:
            cur.execute(
                "INSERT INTO Fuente (nombre_fuente, url_fuente) VALUES (%s, %s) RETURNING id_fuente;",
                (nombre_fuente, url_fuente)
            )
            conn.commit()
            return cur.fetchone()[0]

def get_or_create_zona(conn, nombre_zona):
    """Busca o crea una zona en la DB y retorna su ID."""
    with conn.cursor() as cur:
        cur.execute("SELECT id_zona FROM Zona WHERE nombre_zona = %s;", (nombre_zona,))
        res = cur.fetchone()
        if res:
            return res[0]
        else:
            cur.execute(
                "INSERT INTO Zona (nombre_zona) VALUES (%s) RETURNING id_zona;",
                (nombre_zona,)
            )
            conn.commit()
            return cur.fetchone()[0]

def get_or_create_tipo_inmueble(conn, nombre_tipo_inmueble):
    """Busca o crea un tipo de inmueble en la DB y retorna su ID."""
    with conn.cursor() as cur:
        cur.execute("SELECT id_tipo_inmueble FROM Tipo_Inmueble WHERE nombre_tipo_inmueble = %s;", (nombre_tipo_inmueble,))
        res = cur.fetchone()
        if res:
            return res[0]
        else:
            cur.execute(
                "INSERT INTO Tipo_Inmueble (nombre_tipo_inmueble) VALUES (%s) RETURNING id_tipo_inmueble;",
                (nombre_tipo_inmueble,)
            )
            conn.commit()
            return cur.fetchone()[0]

def insert_inmueble(conn, data):
    """Inserta un registro de inmueble en la DB. data es un diccionario."""
    with conn.cursor() as cur:
        # data: {'id_fuente': int, 'id_zona': int, 'id_tipo_inmueble': int, 
        #        'precio_quetzales': float, 'area_metros': float, 
        #        'habitaciones': int, 'baños': float, 'parqueos': int, 'url': str}
        query = """
        INSERT INTO Inmueble (id_fuente, id_zona, id_tipo_inmueble, precio_quetzales, area_metros, habitaciones, baños, parqueos, url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cur.execute(query, (
            data.get('id_fuente'),
            data.get('id_zona'),
            data.get('id_tipo_inmueble'),
            data.get('precio_quetzales'),
            data.get('area_metros'),
            data.get('habitaciones'),
            data.get('baños'),
            data.get('parqueos'),
            data.get('url')
        ))
        conn.commit()
