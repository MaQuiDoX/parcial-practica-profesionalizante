/* ===== VALIDACIÓN FORMULARIO HTML5 ===== */
const form = document.getElementById('formContacto');
const alertExito = document.getElementById('alertExito');

form.addEventListener('submit', function (e) {
    e.preventDefault();

    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
    }

    // Simular envío
    const btn = form.querySelector('.btn-enviar');
    btn.disabled = true;
    btn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Enviando…';

    setTimeout(() => {
        form.reset();
        form.classList.remove('was-validated');
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-send-fill me-2"></i>Enviar mensaje';
        alertExito.classList.add('show');

        setTimeout(() => alertExito.classList.remove('show'), 6000);
    }, 1200);
});

/* ===== ANIMACIONES SCROLL ===== */
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.12 });

document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));

/* ===== NAVBAR SHADOW ON SCROLL ===== */
window.addEventListener('scroll', () => {
    const nav = document.querySelector('.navbar-huellitas');
    nav.style.boxShadow = window.scrollY > 10
        ? '0 4px 20px rgba(45,27,14,.12)'
        : '0 2px 16px rgba(45,27,14,.08)';
});
