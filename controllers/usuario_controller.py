from flask import request, redirect, url_for, Blueprint, flash,session
from models.usuario_model import Usuario
from views import usuario_view
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash

usuario_bp = Blueprint('usuario', __name__, url_prefix='/usuarios')

@usuario_bp.route('/sistema')
@login_required
def sistema():
    return usuario_view.sistema()

@usuario_bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    usuario = Usuario.query.filter_by(username=username).first()

    if usuario and check_password_hash(usuario.password, password):
        login_user(usuario)
        session['tipo_usuario'] = 'usuario'  # esto es clave
        # redirigir según rol...
        flash("Inicio de sesión exitoso", "user_exito")

        if usuario.rol == 'administrador':
            return redirect(url_for('usuario.sistema'))
        elif usuario.rol == 'recepcionista': 
            return redirect(url_for('usuario.sistema'))
        else:
            flash("Rol no reconocido", "user_error")
            return redirect(url_for('inicio') + '#loginUsuario')

    else:
        flash("Credenciales inválidas", "user_error")
        return redirect(url_for('inicio') + '#loginUsuario')
    
    
@usuario_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('tipo_usuario', None)
    return redirect(url_for('inicio'))


@usuario_bp.route('/')
@login_required
def index():
    usuarios = Usuario.get_all()
    return usuario_view.list(usuarios)


@usuario_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        rol = request.form.get('rol', '').strip()

        if not nombre or not username or not password or not rol:
            flash('Todos los campos son obligatorios.', 'error')
            return usuario_view.create()

        usuario = Usuario(nombre, username, password, rol)
        usuario.save()
        flash('Usuario creado correctamente.', 'success')
        return redirect(url_for('usuario.index'))
    return usuario_view.create()



@usuario_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    usuario = Usuario.get_by_id(id)
    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('usuario.index'))
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        rol = request.form.get('rol', '').strip()

        usuario.update(
            nombre=nombre or usuario.nombre,
            username=username or usuario.username,
            password=password or None,
            rol=rol or usuario.rol
        )
        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('usuario.index'))
    return usuario_view.edit(usuario)

@usuario_bp.route('/delete/<int:id>')
def delete(id):
    usuario = Usuario.get_by_id(id)
    if usuario:
        usuario.delete()
        flash('Usuario eliminado correctamente.', 'success')
    else:
        flash('Usuario no encontrado.', 'error')
    return redirect(url_for('usuario.index'))
