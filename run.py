from flask import Flask, render_template, request, redirect, url_for, session
from database import db
from controllers import cliente_controller, usuario_controller, habitacion_controller,servicio_controller, reserva_controller, reserva_servicio_controller
from flask_login import LoginManager
from models.cliente_model import Cliente
from models.usuario_model import Usuario
from models.reserva_model import Reserva
from datetime import date

app = Flask(__name__)
app.secret_key = 'clave_secreta'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hotel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Login Manager
login_manager = LoginManager()
login_manager.login_view = 'inicio'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    tipo = session.get('tipo_usuario')  # puede ser 'cliente' o 'usuario'

    if tipo == 'cliente':
        return Cliente.query.get(int(user_id))
    elif tipo == 'usuario':
        return Usuario.query.get(int(user_id))
    return None

# Inyectar automáticamente usuario o cliente en todas las plantillas
@app.context_processor
def inject_user_or_client():
    from flask_login import current_user
    if current_user.is_authenticated:
        if hasattr(current_user, 'rol'):
            return dict(usuario=current_user, cliente=None)
        else:
            return dict(usuario=None, cliente=current_user)
    return dict(usuario=None, cliente=None)



# Blueprints
app.register_blueprint(cliente_controller.cliente_bp)
app.register_blueprint(usuario_controller.usuario_bp)
app.register_blueprint(habitacion_controller.habitacion_bp)
app.register_blueprint(servicio_controller.servicio_bp)
app.register_blueprint(reserva_controller.reserva_bp)
app.register_blueprint(reserva_servicio_controller.reserva_servicio_bp)

# Context processor para navbar activo
@app.context_processor
def inject_active_path():
    def is_active(path):
        return 'active' if request.path == path else ''
    return dict(is_active=is_active)

# Rutas básicas
@app.route('/')
def index():
    return redirect(url_for('inicio'))

@app.route('/inicio')
def inicio():
    return render_template('pagina/index.html')

@app.route('/quienes_somos')
def quienes_somos():
    return render_template('pagina/quienes_somos.html')

@app.route('/servicios')
def servicios():
    return render_template('pagina/servicios.html')

@app.route('/noticias')
def noticias():
    return render_template('pagina/noticias.html')

@app.route('/contacto')
def contacto():
    return render_template('pagina/contacto.html')

# Inicialización y creación del usuario si no existe
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Verificar si ya existe un usuario administrador
        if not Usuario.query.filter_by(username='admin').first():
            nuevo_usuario = Usuario(
                nombre='Developer Admin',
                username='admin', #usuario por defecto
                password='admin', #contraseña por defecto
                rol='administrador'
            )
            nuevo_usuario.save()
            print('Usuario administrador creado.')
        else:
            print('El usuario administrador ya existe.')

    app.run(debug=True)
