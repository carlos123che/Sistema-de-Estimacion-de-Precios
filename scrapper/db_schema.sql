-- Crear tabla Fuente
CREATE TABLE IF NOT EXISTS Fuente (
    id_fuente SERIAL PRIMARY KEY,
    nombre_fuente VARCHAR(255) NOT NULL,
    url_fuente VARCHAR(255) NOT NULL
);

-- Crear tabla Tipo_Inmueble
CREATE TABLE IF NOT EXISTS Tipo_Inmueble (
    id_tipo_inmueble SERIAL PRIMARY KEY,
    nombre_tipo_inmueble VARCHAR(255) NOT NULL
);

-- Crear tabla Zona
CREATE TABLE IF NOT EXISTS Zona (
    id_zona SERIAL PRIMARY KEY,
    nombre_zona VARCHAR(255) NOT NULL
);

-- Crear tabla Inmueble
CREATE TABLE IF NOT EXISTS Inmueble (
    id_inmueble SERIAL PRIMARY KEY,
    id_fuente INT NOT NULL,
    id_zona INT,
    id_tipo_inmueble INT,
    precio_quetzales NUMERIC(15, 2),
    area_metros NUMERIC(10, 2),
    habitaciones INT,
    baños NUMERIC(4, 1),
    parqueos INT,
    fecha_extraccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_fuente
        FOREIGN KEY(id_fuente) 
        REFERENCES Fuente(id_fuente)
        ON DELETE CASCADE,
    CONSTRAINT fk_zona
        FOREIGN KEY(id_zona) 
        REFERENCES Zona(id_zona)
        ON DELETE SET NULL,
    CONSTRAINT fk_tipo_inmueble
        FOREIGN KEY(id_tipo_inmueble) 
        REFERENCES Tipo_Inmueble(id_tipo_inmueble)
        ON DELETE SET NULL
);
