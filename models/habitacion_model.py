from database import db

class Habitacion(db.Model):
    __tablename__ = 'habitaciones'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10), nullable=False, unique=True)
    tipo = db.Column(db.String(50), nullable=False)  # Ej: "Simple", "Doble", "Suite"
    precio = db.Column(db.Float(11,2), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='Disponible')  # Ej: Disponible, Ocupada, Mantenimiento

    reservas = db.relationship('Reserva', back_populates='habitacion')

    def __init__(self, numero, tipo, precio, estado='Disponible'):
        self.numero = numero
        self.tipo = tipo
        self.precio = precio
        self.estado = estado

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Habitacion.query.all()
    
    @staticmethod
    def get_by_id(id):
        return Habitacion.query.get(id)

    def update(self, numero=None, tipo=None, precio=None, estado=None):
        if numero:
            self.numero = numero
        if tipo:
            self.tipo = tipo
        if precio is not None:
            self.precio = precio
        if estado:
            self.estado = estado
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
