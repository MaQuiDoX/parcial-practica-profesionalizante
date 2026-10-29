# Documentación actualizada del prototipo

## Objetivo y alcance

El primer parcial presentaba cinco páginas estáticas de Huellitas, con navegación,
Bootstrap, estilos propios, fotos y un formulario simulado. Esta entrega mantiene
el diseño y agrega servidor, persistencia, lógica de cliente y seguridad básica.
Este documento registra la continuidad del prototipo; no se recibió otro documento
del primer parcial.

Recorrido de una petición: navegador → Flask → Peewee → SQLite → HTML o JSON.
JavaScript utiliza `fetch` para actualizar el cliente. Se eligieron pocas herramientas
para poder explicar el proyecto en primer año.

## Aportes de las tres especialidades y rúbrica

| Especialidad | Implementación | Evidencia |
|---|---|---|
| Desarrollo de Software | HTML/Jinja, CSS externo, Bootstrap, buscador con filtros y favoritos, consultas persistentes, Flask y ORM | `src/`, `app.py`, `models.py` |
| Redes y Ciberseguridad | HTTP cliente/servidor, sesiones firmadas, CSRF, CSP contra XSS, protección contra clickjacking, límites por IP y validación | `app.py` y pruebas |
| IA y Ciencia de Datos | Catálogo estructurado, estadísticas y recomendador explicable por reglas | `datos/mascotas.json` y APIs de datos |
| Documentación | Actualización del prototipo, manual, endpoints y modelo físico | README y `docs/` |

La característica inteligente es un recomendador por reglas; también se incluye
un CAPTCHA aritmético educativo. No se utiliza aprendizaje automático ni servicios
de IA pagos. Las reglas pueden explicarse y modificarse durante la defensa.

## Red y seguridad

- El servidor escucha en `127.0.0.1:5000`, accesible solo desde esta computadora.
  El navegador usa HTTP con GET para leer y POST para modificar. Cliente y servidor
  comparten origen, por lo que no se habilita CORS.
- Flask firma la cookie para detectar modificaciones; no la cifra. Contiene favoritos,
  datos CSRF y el desafío, sin emails ni mensajes. Son sesiones anónimas, sin login.
  `HttpOnly` impide leer la cookie desde JS y `SameSite=Lax` restringe su envío entre sitios.
  Expira después de una hora sin actividad. La clave proviene de `SECRET_KEY` o de
  `instance/secret.key`, creada automáticamente y excluida de Git.
- Flask-WTF verifica un token CSRF en todos los POST. Jinja lo coloca en el formulario
  y en una meta; JS lo envía en `X-CSRFToken`. Sin un token válido se responde 400.
- Jinja escapa el texto y JS usa `textContent`. La CSP solo permite scripts propios
  y de jsDelivr, sin JavaScript inline. Peewee genera SQL parametrizado para tratar
  los valores como datos y evitar que se ejecuten como instrucciones.
- `X-Frame-Options: DENY` y `frame-ancestors 'none'` impiden incrustar nuestra página
  en otro sitio. La CSP permite mostrar el mapa de Google dentro de Contacto.
- Flask-Limiter aplica 5 consultas/minuto y 30 cambios de favoritos/minuto por IP,
  además de 200 solicitudes/minuto por ruta e IP. Al superar el límite responde 429.
  Esto mitiga intentos repetidos y spam; no existe login para atacar contraseñas.
  El almacenamiento de límites en memoria es para una demo en un solo proceso.
- El CAPTCHA se verifica en el servidor y se consume al guardar. Es educativo:
  un bot puede resolver la suma y la sesión firmada es legible. Si abrís varias
  pestañas de Contacto, todas comparten el desafío de la última carga.
- Se validan formato, longitudes, motivo y CAPTCHA en el servidor aunque JS esté
  desactivado. El cuerpo máximo es 16 KiB. No hay una API pública que lea consultas.

Para una eventual práctica con HTTPS, `HTTPS=1` activa cookie `Secure` y HSTS.
No activarlo en la demo HTTP: el navegador no enviaría la cookie segura.
Un despliegue público requiere HTTPS, servidor WSGI, clave propia y límites compartidos.
El servidor de desarrollo permanece local y con debug desactivado.

## Endpoints

| Método | Ruta | Entrada | Respuesta |
|---|---|---|---|
| GET | `/`, `/index.html` | Ninguna | Inicio con estadísticas |
| GET | `/perros.html`, `/gatos.html` | Ninguna | Catálogo desde SQLite |
| GET | `/adopcion.html` | Ninguna | Proceso y recomendador |
| GET | `/contacto.html` | Ninguna | Formulario, token CSRF y nuevo CAPTCHA |
| GET | `/static/<archivo>` | Ruta CSS, JS o imagen | Recurso estático |
| GET | `/api/estadisticas` | Ninguna | JSON `total`, `perros`, `gatos`, `cachorros` |
| GET | `/api/recomendaciones` | Query `especie` (perro/gato), `energia` (tranquila/activa) | JSON `resultados`, máximo 3; 400 si las preferencias no son válidas |
| POST | `/api/favoritos/<id>` | Cookie y cabecera `X-CSRFToken` | JSON `favoritos`: lista de IDs; 404 si no existe |
| POST | `/api/consultas` | FormData: `nombre`, `email`, `telefono`, `motivo`, `mensaje`, `captcha`, `csrf_token` | 201 JSON `mensaje` y `numero`; 400 si la validación falla |

Los POST necesitan cookie y token CSRF correspondiente. Los errores esperados de
API incluyen `error` en JSON. Se responde 413 por cuerpo demasiado grande y 429
por exceso de intentos. Las páginas no permitidas devuelven 404.

Ejemplo: `GET /api/recomendaciones?especie=perro&energia=tranquila` devuelve objetos
con `id`, `nombre`, `puntos`, `razon` y `descripcion` dentro de `resultados`.

## Modelo físico

SQLite guarda los datos en `instance/huellitas.db`. Peewee crea las tablas de
`models.py`. [modelo.sql](modelo.sql) contiene el SQL de referencia.

| Tabla | Campos (todos NOT NULL) | Uso |
|---|---|---|
| `mascota` | `id INTEGER PK`, `nombre VARCHAR(80)`, `especie VARCHAR(10)`, `imagen VARCHAR(255)`, `descripcion TEXT`, `edad_meses INTEGER`, `tamano VARCHAR(10)`, `energia VARCHAR(10)` | Catálogo y atributos de recomendación |
| `consulta` | `id INTEGER PK`, `nombre VARCHAR(80)`, `email VARCHAR(120)`, `telefono VARCHAR(30)`, `motivo VARCHAR(80)`, `mensaje TEXT`, `creada DATETIME` | Consultas con fecha UTC del servidor |

El teléfono opcional se guarda como cadena vacía y SQLite asigna los IDs.
No hay claves foráneas: las consultas son generales, sin mascota obligatoria.
Los favoritos se guardan en la sesión, sin tabla de usuarios.
SQLite no impone longitudes VARCHAR: las valida el servidor.

## Datos y reglas

Los 16 registros iniciales proceden de las tarjetas. La edad se normaliza a meses.
Tamaño y energía son categorías ilustrativas y deben verificarse con el refugio.
«Pedro y Pitufino» es una ficha de una pareja: las estadísticas cuentan fichas,
no animales individuales auditados. Inicialmente hay 8 perros, 8 gatos y 8 fichas
de menores de un año. La carga inicial solo se realiza si el catálogo está vacío.

El recomendador asigna 2 puntos por especie y 1 por actividad, descarta especies
diferentes, ordena por puntaje descendente y nombre ascendente y devuelve los tres
primeros con una explicación. No reemplaza la entrevista de adopción.

## Comprobaciones

`python -m unittest discover -s tests -v` usa SQLite temporal para verificar páginas,
recursos, estadísticas, recomendación, consultas, validaciones, CSRF, CAPTCHA de un
solo uso, favoritos por sesión, límites, cabeceras, SQL parametrizado y escape HTML.

## Fuentes técnicas

- [Seguridad de Flask](https://flask.palletsprojects.com/en/stable/web-security/)
- [CSRF con Flask-WTF](https://flask-wtf.readthedocs.io/en/latest/csrf/)
- [Tablas con Peewee](https://docs.peewee-orm.com/en/latest/peewee/schema.html)
- [Flask-Limiter](https://flask-limiter.readthedocs.io/en/latest/)
