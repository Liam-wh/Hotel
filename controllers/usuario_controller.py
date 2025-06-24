from flask import request, redirect, url_for, Blueprint, flash, session, render_template, make_response, current_app
from models.usuario_model import Usuario
from views import usuario_view
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from database import db 
import pdfkit
import os

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
            return redirect(url_for('usuario.index'))
        
        # Verificar si el username ya existe
        usuario_existente = Usuario.query.filter_by(username=username).first()
        if usuario_existente:
            flash('El nombre de usuario ya está en uso. Intente con otro.', 'warning')
            return redirect(url_for('usuario.index'))

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




@usuario_bp.route('/perfil')
@login_required
def perfil_usuario():
    if not hasattr(current_user, 'rol'):
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('inicio'))
    return render_template('usuarios/perfil.html', usuario=current_user)


@usuario_bp.route('/perfil/cambiar_password', methods=['POST'])
@login_required
def cambiar_password():
    actual = request.form['actual']
    nueva1 = request.form['nueva1']
    nueva2 = request.form['nueva2']

    if not current_user.verify_password(actual):
        flash('La contraseña actual es incorrecta.', 'danger')
        return redirect(url_for('usuario.perfil_usuario'))

    if nueva1 != nueva2:
        flash('Las nuevas contraseñas no coinciden.', 'warning')
        return redirect(url_for('usuario.perfil_usuario'))

    current_user.set_password(nueva1)
    current_user.save()
    flash('Contraseña actualizada correctamente.', 'success')
    return redirect(url_for('usuario.perfil_usuario'))


@usuario_bp.route('/perfil/restablecer_password', methods=['POST'])
@login_required
def restablecer_password():
    import random, string
    nueva = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    current_user.set_password(nueva)
    current_user.save()
    flash(f'Tu nueva contraseña es: {nueva}', 'info')
    return redirect(url_for('usuario.perfil_usuario'))




@usuario_bp.route('/perfil/actualizar', methods=['POST'])
@login_required
def actualizar_perfil():
    usuario = Usuario.query.get(current_user.id)

    if usuario:
        usuario.nombre = request.form.get('nombre', '').strip()
        usuario.username = request.form.get('username', '').strip()
        db.session.commit()
        flash('Perfil actualizado correctamente.', 'success')
    else:
        flash('No se pudo actualizar el perfil.', 'danger')

    return redirect(url_for('usuario.perfil_usuario'))




@usuario_bp.route('/reporte/pdf')
@login_required
def reporte_pdf():
    usuarios = Usuario.get_all()

    # ✅ Ruta absoluta local a la imagen (no usar URL externa)
    modelo_path = os.path.join(current_app.root_path, 'static', 'images', 'modelo_pdf.jpg')
    modelo_url = 'file://' + modelo_path

    html = render_template('pdf/usuarios_pdf.html', usuarios=usuarios, modelo_url=modelo_url)

    options = {
        'enable-local-file-access': '',
        'page-size': 'Letter',
        'margin-top': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
        'margin-right': '0mm',
        'encoding': "UTF-8",
        'print-media-type': '',  # Para mostrar fondos definidos en CSS
        'no-outline': None
    }

    pdf = pdfkit.from_string(html, False, options=options)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=reporte_usuarios.pdf'

    return response
