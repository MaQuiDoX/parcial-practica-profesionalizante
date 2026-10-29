# Huellitas en busca de un hogar

Proyecto educativo de Práctica Profesionalizante I, IES 9-008 «Manuel Belgrano», Mendoza.
Aplicación de refugio con Flask, HTML/Jinja, CSS, Bootstrap, JavaScript y SQLite.
Mantiene el diseño del primer parcial y suma funciones sencillas para primer año.

## Ejecutar en Windows

Necesitás Python 3.10 o posterior. Desde la carpeta del proyecto:

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python app.py
```

Abrí **http://127.0.0.1:5000**. Detené el servidor con `Ctrl+C`.
Usá el servidor: abrir los HTML con doble clic ya no renderiza las plantillas Jinja.
SQLite crea automáticamente `instance/huellitas.db` con 16 fichas de demostración.
Bootstrap, fuentes y mapa necesitan Internet.

## Funciones

- Buscador por nombre o descripción, filtros combinados y favoritos en la sesión.
- Consultas validadas y almacenadas en SQLite, con CAPTCHA aritmético educativo.
- Recomendador explicable por especie y actividad, sin modelos entrenados.
- Estadísticas del catálogo y protecciones CSRF, CSP y límites de solicitudes.

Los mensajes se guardan localmente; no se envían emails. Los datos son de demostración.
Las sesiones son anónimas: no hace falta crear una cuenta ni hay contraseñas.

## Archivos

| Archivo o carpeta | Responsabilidad |
|---|---|
| `app.py` | Rutas, validación, sesiones, seguridad y recomendación |
| `models.py` | Tablas Peewee/SQLite |
| `requirements.txt` | Dependencias |
| `src/*.html` | Plantillas |
| `src/css/`, `src/js/app.js` | Estilos y lógica externa de cliente |
| `datos/mascotas.json` | Catálogo inicial |
| `docs/` | Documentación de la rúbrica |
| `tests/` | Pruebas con base temporal |
| `instance/` | Base y clave local, excluidas de Git |

## Documentación y pruebas

- [Manual de usuario](docs/manual-usuario.md)
- [Documentación, endpoints y aportes de las tres especialidades](docs/documentacion.md)
- [Modelo físico SQL](docs/modelo.sql)

```powershell
.venv\Scripts\python -m unittest discover -s tests -v
```

Servidor local de demostración en un solo proceso y sin debug. Los límites se guardan
en memoria y se reinician con el servidor. Para un despliegue público se necesitan
HTTPS, servidor WSGI, clave propia y límites compartidos; quedan fuera del ejercicio.
