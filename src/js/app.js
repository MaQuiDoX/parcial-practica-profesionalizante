/* Funciones de cliente compartidas. Los datos del usuario se muestran con textContent. */
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

async function pedir(url, opciones = {}) {
    const respuesta = await fetch(url, opciones);
    const datos = await respuesta.json();
    if (!respuesta.ok) throw new Error(datos.error || 'No se pudo completar la operación.');
    return datos;
}

window.addEventListener('scroll', () => {
    document.querySelector('.navbar-huellitas')?.classList.toggle('con-sombra', window.scrollY > 10);
}, { passive: true });

// Buscar y combinar filtros sin volver a cargar la página.
const fichas = [...document.querySelectorAll('.ficha-mascota')];
function filtrar() {
    const normalizar = texto => texto.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    const busqueda = normalizar(document.getElementById('buscar').value);
    const edad = document.getElementById('edad').value;
    const soloFavoritos = document.getElementById('solo-favoritos').checked;
    let visibles = 0;
    fichas.forEach(ficha => {
        const cachorro = Number(ficha.dataset.edad) < 12;
        const coincide = normalizar(ficha.querySelector('h3').textContent + ' ' + ficha.querySelector('.pet-meta').textContent).includes(busqueda);
        const edadValida = edad === 'todos' || (edad === 'cachorro' ? cachorro : !cachorro);
        const favorito = ficha.querySelector('.favorito').getAttribute('aria-pressed') === 'true';
        ficha.hidden = !(coincide && edadValida && (!soloFavoritos || favorito));
        if (!ficha.hidden) visibles++;
    });
    document.getElementById('resultado-busqueda').textContent = visibles === 1 ? '1 mascota encontrada.' : visibles ? `${visibles} mascotas encontradas.` : 'No hay coincidencias. Probá otros filtros.';
}
if (fichas.length) {
    ['buscar', 'edad', 'solo-favoritos'].forEach(id => document.getElementById(id).addEventListener('input', filtrar));
    filtrar();
}
document.querySelectorAll('.favorito').forEach(boton => {
    boton.addEventListener('click', async () => {
        boton.disabled = true;
        const estado = document.getElementById('error-catalogo');
        estado.textContent = '';
        try {
            const datos = await pedir(`/api/favoritos/${boton.dataset.id}`, { method: 'POST', headers: { 'X-CSRFToken': csrfToken } });
            const guardado = datos.favoritos.includes(Number(boton.dataset.id));
            boton.setAttribute('aria-pressed', String(guardado));
            boton.textContent = guardado ? '♥ Favorito' : '♡ Guardar';
            filtrar();
        } catch (error) { estado.textContent = error.message; }
        finally { boton.disabled = false; }
    });
});

const contacto = document.getElementById('formContacto');
contacto?.addEventListener('submit', async evento => {
    evento.preventDefault();
    if (!contacto.reportValidity()) return;
    const boton = contacto.querySelector('button[type="submit"]');
    const estado = document.getElementById('estado-contacto');
    boton.disabled = true;
    estado.textContent = 'Guardando consulta…';
    try {
        const datos = await pedir(contacto.action, { method: 'POST', body: new FormData(contacto), headers: { 'X-CSRFToken': csrfToken } });
        estado.textContent = `${datos.mensaje} Número de consulta: ${datos.numero}. Recargá la página para enviar otra.`;
        contacto.reset();
        // El CAPTCHA es de un solo uso; el botón queda deshabilitado tras el éxito.
    } catch (error) {
        estado.textContent = error.message || 'No hay conexión. Intentá nuevamente.';
        boton.disabled = false;
    }
});

document.getElementById('formRecomendador')?.addEventListener('submit', async evento => {
    evento.preventDefault();
    const salida = document.getElementById('recomendaciones');
    const boton = evento.target.querySelector('button');
    boton.disabled = true;
    salida.textContent = 'Buscando coincidencias…';
    try {
        const parametros = new URLSearchParams(new FormData(evento.target));
        const datos = await pedir(`/api/recomendaciones?${parametros}`);
        salida.replaceChildren();
        datos.resultados.forEach(mascota => {
            const parrafo = document.createElement('p');
            parrafo.textContent = `${mascota.nombre}: ${mascota.puntos}/3 puntos. ${mascota.razon} ${mascota.descripcion}`;
            salida.append(parrafo);
        });
        if (!datos.resultados.length) salida.textContent = 'No hay mascotas disponibles con esas preferencias.';
    } catch (error) { salida.textContent = error.message; }
    finally { boton.disabled = false; }
});
