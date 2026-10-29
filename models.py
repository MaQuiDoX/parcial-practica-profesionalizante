"""Dos tablas SQLite, manejadas con el ORM Peewee."""
from datetime import datetime, timezone
from peewee import Model, SqliteDatabase, CharField, TextField, IntegerField, DateTimeField

db = SqliteDatabase(None)


class BaseModel(Model):
    class Meta:
        database = db


class Mascota(BaseModel):
    nombre = CharField(max_length=80)
    especie = CharField(max_length=10)
    imagen = CharField()
    descripcion = TextField()
    edad_meses = IntegerField()
    tamano = CharField(max_length=10)
    energia = CharField(max_length=10)


class Consulta(BaseModel):
    nombre = CharField(max_length=80)
    email = CharField(max_length=120)
    telefono = CharField(max_length=30, default='')
    motivo = CharField(max_length=80)
    mensaje = TextField()
    creada = DateTimeField(default=lambda: datetime.now(timezone.utc))
