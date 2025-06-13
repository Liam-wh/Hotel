from database import db

class ReservaServicio(db.Model):
    __tablename__ = 'reserva_servicios'

    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=1)

    def __init__(self, reserva_id, servicio_id, cantidad=1):
        self.reserva_id = reserva_id
        self.servicio_id = servicio_id
        self.cantidad = cantidad

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return ReservaServicio.query.all()

    @staticmethod
    def get_by_id(id):
        return ReservaServicio.query.get(id)

    def update(self, reserva_id=None, servicio_id=None, cantidad=None):
        if reserva_id:
            self.reserva_id = reserva_id
        if servicio_id:
            self.servicio_id = servicio_id
        if cantidad is not None:
            self.cantidad = cantidad
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
