-- Referencia del modelo físico. Peewee crea las tablas al iniciar app.py.
CREATE TABLE mascota (
    id INTEGER PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    especie VARCHAR(10) NOT NULL,
    imagen VARCHAR(255) NOT NULL,
    descripcion TEXT NOT NULL,
    edad_meses INTEGER NOT NULL,
    tamano VARCHAR(10) NOT NULL,
    energia VARCHAR(10) NOT NULL
);

CREATE TABLE consulta (
    id INTEGER PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    email VARCHAR(120) NOT NULL,
    telefono VARCHAR(30) NOT NULL,
    motivo VARCHAR(80) NOT NULL,
    mensaje TEXT NOT NULL,
    creada DATETIME NOT NULL
);
