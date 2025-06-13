from database import db

class Reserva(db.Model):
    __tablename__ = 'reservas'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    habitacion_id = db.Column(db.Integer, db.ForeignKey('habitaciones.id'), nullable=False)
    fecha_entrada = db.Column(db.Date, nullable=False)
    fecha_salida = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20), nullable=False)  # Ejemplo: 'Confirmada', 'Cancelada', 'Pendiente'
    total = db.Column(db.Float, nullable=False)    # Total de la reserva: precio + servicios

    # Relaciones
    cliente = db.relationship('Cliente', back_populates='reservas')
    habitacion = db.relationship('Habitacion', back_populates='reservas')
    servicios = db.relationship('ReservaServicio', back_populates='reserva', cascade="all, delete-orphan")

    def __init__(self, cliente_id, habitacion_id, fecha_entrada, fecha_salida, estado, total):
        self.cliente_id = cliente_id
        self.habitacion_id = habitacion_id
        self.fecha_entrada = fecha_entrada
        self.fecha_salida = fecha_salida
        self.estado = estado
        self.total = total

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Reserva.query.all()

    @staticmethod
    def get_by_id(id):
        return Reserva.query.get(id)

    def update(self, cliente_id=None, habitacion_id=None, fecha_entrada=None, fecha_salida=None, estado=None, total=None):
        if cliente_id:
            self.cliente_id = cliente_id
        if habitacion_id:
            self.habitacion_id = habitacion_id
        if fecha_entrada:
            self.fecha_entrada = fecha_entrada
        if fecha_salida:
            self.fecha_salida = fecha_salida
        if estado:
            self.estado = estado
        if total is not None:
            self.total = total
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
