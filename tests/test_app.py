"""Pruebas de integración con SQLite temporal; ejecutar con unittest."""
import re
import tempfile
import unittest
from pathlib import Path
from app import create_app
from models import Consulta, Mascota, db


class AplicacionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporal = tempfile.TemporaryDirectory()
        cls.app = create_app({'TESTING': True, 'SECRET_KEY': 'clave-solo-para-tests',
                              'DATABASE': str(Path(cls.temporal.name) / 'pruebas.db')})

    @classmethod
    def tearDownClass(cls):
        if not db.is_closed():
            db.close()
        cls.temporal.cleanup()

    def setUp(self):
        self.client = self.app.test_client()
        for limiter in self.app.extensions['limiter']:
            limiter.reset()
        with db.connection_context():
            Consulta.delete().execute()

    def formulario(self):
        html = self.client.get('/contacto.html').get_data(as_text=True)
        token = re.search(r'name="csrf-token" content="([^"]+)"', html)[1]
        with self.client.session_transaction() as sesion:
            captcha = sesion['captcha']
        return dict(nombre='Ana Pérez', email='ana@example.com', telefono='',
                    motivo='Quiero adoptar un perro', mensaje='Quisiera conocer a Lupita.',
                    captcha=str(captcha), csrf_token=token)

    def test_paginas_y_archivos(self):
        for pagina in ('/', '/index.html', '/perros.html', '/gatos.html', '/adopcion.html', '/contacto.html'):
            respuesta = self.client.get(pagina)
            self.assertEqual(respuesta.status_code, 200, pagina)
            html = respuesta.get_data(as_text=True)
            self.assertNotIn('{{', html)
            for url in re.findall(r'(?:href|src)="(/static/[^"]+)"', html):
                with self.client.get(url) as recurso:
                    self.assertEqual(recurso.status_code, 200, url)
        self.assertEqual(self.client.get('/desconocida.html').status_code, 404)

    def test_datos_y_recomendaciones(self):
        datos = self.client.get('/api/estadisticas').json
        self.assertEqual(datos, dict(total=16, perros=8, gatos=8, cachorros=8))
        resultados = self.client.get('/api/recomendaciones?especie=perro&energia=tranquila').json['resultados']
        self.assertEqual(len(resultados), 3)
        self.assertEqual(resultados[0]['puntos'], 3)
        self.assertIn(resultados[0]['nombre'], ('Canela', 'Max'))
        self.assertEqual(self.client.get('/api/recomendaciones?especie=ave').status_code, 400)

    def test_contacto_persiste_y_no_reutiliza_captcha(self):
        formulario = self.formulario()
        self.assertEqual(self.client.post('/api/consultas', data=formulario).status_code, 201)
        with db.connection_context():
            self.assertEqual(Consulta.select().count(), 1)
            self.assertEqual(Consulta.get().nombre, 'Ana Pérez')
        self.assertEqual(self.client.post('/api/consultas', data=formulario).status_code, 400)

    def test_csrf_captcha_y_validacion(self):
        formulario = self.formulario()
        sin_token = {k: v for k, v in formulario.items() if k != 'csrf_token'}
        self.assertEqual(self.client.post('/api/consultas', data=sin_token).status_code, 400)
        for campo, valor in [('captcha', '999'), ('captcha', '9' * 5000), ('email', 'incorrecto'), ('mensaje', 'a' * 2001)]:
            self.assertEqual(self.client.post('/api/consultas', data={**formulario, campo: valor}).status_code, 400)
        with db.connection_context():
            self.assertEqual(Consulta.select().count(), 0)

    def test_favoritos_persisten_y_estan_aislados(self):
        token = self.formulario()['csrf_token']
        headers = {'X-CSRFToken': token}
        self.assertEqual(self.client.post('/api/favoritos/1').status_code, 400)
        self.assertEqual(self.client.post('/api/favoritos/1', headers=headers).json['favoritos'], [1])
        self.assertIn('aria-pressed="true"', self.client.get('/perros.html').get_data(as_text=True))
        otro = self.app.test_client()
        self.assertNotIn('aria-pressed="true"', otro.get('/perros.html').get_data(as_text=True))
        self.assertEqual(self.client.post('/api/favoritos/999', headers=headers).status_code, 404)
        self.assertEqual(self.client.post('/api/favoritos/1', headers=headers).json['favoritos'], [])

    def test_limite_intentos(self):
        formulario = self.formulario()
        formulario['captcha'] = '999'
        for _ in range(5):
            self.assertEqual(self.client.post('/api/consultas', data=formulario).status_code, 400)
        self.assertEqual(self.client.post('/api/consultas', data=formulario).status_code, 429)

    def test_cabeceras_y_cookie(self):
        respuesta = self.client.get('/contacto.html')
        self.assertEqual(respuesta.headers['X-Frame-Options'], 'DENY')
        self.assertEqual(respuesta.headers['X-Content-Type-Options'], 'nosniff')
        self.assertIn("script-src 'self'", respuesta.headers['Content-Security-Policy'])
        self.assertNotIn("'unsafe-inline'", respuesta.headers['Content-Security-Policy'])
        self.assertIn('HttpOnly', respuesta.headers['Set-Cookie'])
        self.assertIn('SameSite=Lax', respuesta.headers['Set-Cookie'])

    def test_inyeccion_y_escape(self):
        formulario = self.formulario()
        formulario.update(nombre="Robert'); DROP TABLE mascota;--", mensaje='<script>alert(1)</script>')
        self.assertEqual(self.client.post('/api/consultas', data=formulario).status_code, 201)
        with db.connection_context():
            self.assertEqual(Mascota.select().count(), 16)
            mascota = Mascota.get_by_id(1)
            original = mascota.nombre
            mascota.nombre = '<script>alert(1)</script>'
            mascota.save()
        try:
            html = self.client.get('/perros.html').get_data(as_text=True)
            self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', html)
            self.assertNotIn('<script>alert(1)</script>', html)
        finally:
            with db.connection_context():
                Mascota.update(nombre=original).where(Mascota.id == 1).execute()


if __name__ == '__main__':
    unittest.main()
