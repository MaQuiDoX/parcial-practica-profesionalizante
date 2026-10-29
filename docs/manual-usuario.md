# Manual de usuario

## Inicio

Iniciá el servidor siguiendo el README y entrá a http://127.0.0.1:5000.
El menú permite recorrer Inicio, Perros, Gatos, Adopción y Contacto.
En celulares se abre con el botón de menú. Inicio muestra un resumen del catálogo.
Las cifras históricas de rescates y adopciones son ilustrativas; las cantidades
de fichas disponibles se calculan desde la base de datos.

## Buscar y guardar mascotas

En Perros o Gatos, escribí un nombre o parte de la descripción.
El resultado cambia al escribir e ignora mayúsculas y tildes.
Podés combinarlo con «Menos de un año» o «Un año o más».
La cantidad indica cuántas mascotas cumplen todos los filtros.
Si no hay coincidencias, borrá la búsqueda o elegí otra edad.

Presioná «♡ Guardar» para agregar una mascota a favoritos.
El botón cambia a «♥ Favorito»; otro clic la quita.
Activá «Solo favoritos» para ver los que guardaste en ese catálogo.
Se conservan al navegar y recargar, usando una cookie de sesión.
Expiran después de una hora sin actividad; otro navegador tiene su propia lista.
No se necesita una cuenta. «Consultar adopción» lleva al formulario general.

## Recomendación

En Adopción, buscá «Encontrá un compañero», elegí especie y actividad y presioná
«Recomendar». Aparecen hasta tres opciones, sus puntos y una razón.
Se asignan dos puntos por especie y uno por actividad. Solo se muestran mascotas
de la especie elegida y se ordenan por puntos; los empates se ordenan por nombre.
Los niveles de actividad son datos de ejemplo. La recomendación no reemplaza una
entrevista con el refugio.

## Contacto

Completá nombre, email, motivo, mensaje y la suma de verificación.
El teléfono es opcional. El mensaje debe tener entre 10 y 2000 caracteres.
Presioná «Enviar mensaje» y esperá el resultado debajo del botón.
El número de consulta confirma que se guardó en SQLite; no se envía un email.
El CAPTCHA se consume al guardar. Para enviar otra consulta, recargá la página.

Si la suma está mal, corregila. Si la sesión venció, recargá y completá nuevamente.
Si superás cinco intentos por minuto, esperá un minuto antes de volver a enviar.
Ante un error de conexión, verificá que el servidor siga ejecutándose.
No hay una pantalla pública para leer consultas: permanecen en la base local.

## Demostración para la clase

1. Buscá «Lupita», guardala como favorita y recargá para mostrar la persistencia.
2. Activá «Solo favoritos» y combiná un filtro sin coincidencias.
3. Solicitá perros con actividad tranquila: Canela y Max obtienen tres puntos.
4. Enviá una consulta y anotá su número. Mostrá la tabla `consulta` en un visor SQLite.
5. Ejecutá las pruebas para comprobar CSRF, límites, sesiones y validación.

Usá datos ficticios para las demostraciones del curso.
