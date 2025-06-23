from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Usuario(db.Model,UserMixin):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    

    def __init__(self, nombre, username, password, rol):
        self.nombre = nombre
        self.username = username
        self.password = self.hash_password(password)
        self.rol = rol

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password, password)
    
    # Método para actualizar la contraseña correctamente
    def set_password(self, new_password):
        self.password = self.hash_password(new_password)
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Usuario.query.all()
    
    @staticmethod
    def get_by_id(id):
        return Usuario.query.get(id)
    
    def update(self,nombre=None, username=None, password=None, rol=None):
        if nombre:
            self.nombre = nombre
        if username:
            self.username = username
        if password:
            self.password = self.hash_password(password)
        if rol:
            self.rol = rol
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
