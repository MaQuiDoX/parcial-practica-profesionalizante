"""Servidor educativo. Ejecutar con: py app.py."""
import json
import os
import re
import secrets
from datetime import timedelta
from pathlib import Path

from flask import Flask, jsonify, render_template, request, session, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect, CSRFError
from models import db, Mascota, Consulta

BASE = Path(__file__).resolve().parent
MOTIVOS = ('Quiero adoptar un perro', 'Quiero adoptar un gato',
           'Quiero ser voluntario', 'Quiero donar')


def create_app(test_config=None):
    app = Flask(__name__, template_folder='src', static_folder='src', static_url_path='/static')
    Path(app.instance_path).mkdir(exist_ok=True)
    # La clave local persiste al reiniciar y nunca se agrega al repositorio.
    key_file = Path(app.instance_path) / 'secret.key'
    if not key_file.exists():
        key_file.write_text(secrets.token_hex(32), encoding='utf-8')
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY') or key_file.read_text(encoding='utf-8'),
        DATABASE=str(Path(app.instance_path) / 'huellitas.db'),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=os.environ.get('HTTPS') == '1',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=1),
        MAX_CONTENT_LENGTH=16 * 1024,
    )
    
    if test_config:
        app.config.update(test_config)
    CSRFProtect(app)
    limiter = Limiter(get_remote_address, app=app, storage_uri='memory://',
                      default_limits=['200 per minute'])
    db.init(app.config['DATABASE'], pragmas={'foreign_keys': 1})
    with db.connection_context():
        db.create_tables([Mascota, Consulta])
        if not Mascota.select().exists():
            with db.atomic():
                Mascota.insert_many(json.loads((BASE / 'datos/mascotas.json').read_text(encoding='utf-8'))).execute()

    @app.before_request
    def conectar():
        db.connect(reuse_if_open=True)
        session.permanent = True

    @app.teardown_request
    def cerrar(error=None):
        if not db.is_closed():
            db.close()

    @app.after_request
    def seguridad(response):
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; "
            "style-src 'self' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; "
            "frame-src https://www.google.com; object-src 'none'; "
            "base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
        )
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        if request.endpoint != 'static':
            response.headers['Cache-Control'] = 'no-store'
        if app.config['SESSION_COOKIE_SECURE']:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000'
        return response

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return jsonify(error='La sesión o el formulario venció. Recargá la página.'), 400

    @app.errorhandler(429)
    def demasiados(error):
        return jsonify(error='Demasiados intentos. Esperá un minuto y volvé a probar.'), 429

    @app.errorhandler(413)
    def demasiado_grande(error):
        return jsonify(error='El mensaje es demasiado grande.'), 413

    def estadisticas():
        return dict(total=Mascota.select().count(),
                    perros=Mascota.select().where(Mascota.especie == 'perro').count(),
                    gatos=Mascota.select().where(Mascota.especie == 'gato').count(),
                    cachorros=Mascota.select().where(Mascota.edad_meses < 12).count())

    @app.get('/')
    @app.get('/<pagina>.html')
    def pagina(pagina='index'):
        if pagina not in ('index', 'perros', 'gatos', 'adopcion', 'contacto'):
            abort(404)
        mascotas = Mascota.select().where(Mascota.especie == ('perro' if pagina == 'perros' else 'gato'))
        pregunta = ''
        if pagina == 'contacto':
            a, b = secrets.randbelow(8) + 1, secrets.randbelow(8) + 1
            session['captcha'] = a + b
            pregunta = f'{a} + {b}'
        return render_template(f'{pagina}.html', mascotas=mascotas,
                               favoritos=session.get('favoritos', []),
                               estadisticas=estadisticas(), pregunta=pregunta)

    @app.get('/api/estadisticas')
    def datos():
        return jsonify(estadisticas())

    @app.post('/api/favoritos/<int:mascota_id>')
    @limiter.limit('30 per minute')
    def favorito(mascota_id):
        if not Mascota.get_or_none(Mascota.id == mascota_id):
            return jsonify(error='Mascota inexistente.'), 404
        favoritos = session.get('favoritos', [])
        if mascota_id in favoritos:
            favoritos.remove(mascota_id)
        else:
            favoritos.append(mascota_id)
        session['favoritos'] = favoritos
        return jsonify(favoritos=favoritos)

    @app.post('/api/consultas')
    @limiter.limit('5 per minute')
    def consulta():
        campos = {nombre: request.form.get(nombre, '').strip()
                  for nombre in ('nombre', 'email', 'telefono', 'motivo', 'mensaje')}
        if (not 2 <= len(campos['nombre']) <= 80
                or len(campos['email']) > 120
                or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', campos['email'])
                or len(campos['telefono']) > 30 or campos['motivo'] not in MOTIVOS
                or not 10 <= len(campos['mensaje']) <= 2000):
            return jsonify(error='Revisá los datos: nombre, email, motivo y mensaje de 10 a 2000 caracteres.'), 400
        respuesta = request.form.get('captcha', '')
        if not 1 <= len(respuesta) <= 2 or not respuesta.isascii() or not respuesta.isdigit() or int(respuesta) != session.get('captcha'):
            return jsonify(error='La suma no es correcta. Revisá la respuesta o recargá la página.'), 400
        session.pop('captcha', None)  # Cada desafío se usa una sola vez.
        registro = Consulta.create(**campos)
        return jsonify(mensaje='Consulta guardada en el refugio. No se envía un correo.', numero=registro.id), 201

    @app.get('/api/recomendaciones')
    def recomendaciones():
        especie = request.args.get('especie', '')
        energia = request.args.get('energia', '')
        if especie not in ('perro', 'gato') or energia not in ('tranquila', 'activa'):
            return jsonify(error='Elegí una especie y un nivel de actividad.'), 400
        # Sistema de reglas: 2 puntos por especie y 1 por actividad.
        resultados = []
        for mascota in Mascota.select():
            puntos = 2 * (mascota.especie == especie) + (mascota.energia == energia)
            if mascota.especie == especie:
                resultados.append(dict(id=mascota.id, nombre=mascota.nombre, puntos=puntos,
                                       razon='Coincide la especie' + (' y la actividad.' if puntos == 3 else '.'),
                                       descripcion=mascota.descripcion))
        resultados.sort(key=lambda item: (-item['puntos'], item['nombre']))
        return jsonify(resultados=resultados[:3])

    return app


if __name__ == '__main__':
    create_app().run(host='127.0.0.1', port=5000, debug=False)
