from database import db
from flask_login import UserMixin

class Cliente(db.Model, UserMixin):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    documento = db.Column(db.String(50), unique=True, nullable=False)
    correo = db.Column(db.String(100), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)

    # Relación con Reservas
    reservas = db.relationship('Reserva', back_populates='cliente')

    def __init__(self, nombre, documento, correo=None, telefono=None):
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Cliente.query.all()

    @staticmethod
    def get_by_id(id):
        return Cliente.query.get(id)

    def update(self, nombre=None, documento=None, correo=None, telefono=None):
        if nombre: self.nombre = nombre
        if documento: self.documento = documento
        if correo: self.correo = correo
        if telefono: self.telefono = telefono
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
