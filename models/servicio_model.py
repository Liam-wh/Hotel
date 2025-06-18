from database import db

class Servicio(db.Model):
    __tablename__ = 'servicios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)  # Ejemplo: "Lavandería", "Desayuno", "Spa"
    descripcion = db.Column(db.String(255), nullable=True)
    precio = db.Column(db.Float, nullable=False)

    # Opcional: relación con reservas si quieres registrar servicios usados en una reserva
    res_servicio = db.relationship('ReservaServicio', back_populates='servicio', cascade='all, delete-orphan')

    def __init__(self, nombre, descripcion, precio):
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Servicio.query.all()
    
    @staticmethod
    def get_by_id(id):
        return Servicio.query.get(id)

    def update(self, nombre=None, descripcion=None, precio=None):
        if nombre:
            self.nombre = nombre
        if descripcion:
            self.descripcion = descripcion
        if precio is not None:
            self.precio = precio
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
