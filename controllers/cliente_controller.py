from flask import request, redirect, url_for, Blueprint, flash, session
from flask_login import login_user, logout_user, login_required
from models.cliente_model import Cliente
from views import cliente_view

cliente_bp = Blueprint('cliente', __name__, url_prefix='/clientes')


@cliente_bp.route('/sistema')
@login_required
def sistema():
    return cliente_view.sistema()


@cliente_bp.route('/login', methods=['POST'])
def login():
    correo = request.form.get('correo')
    documento = request.form.get('documento')

    cliente = Cliente.query.filter_by(correo=correo).first()

    if cliente and cliente.documento == documento:  # o check_password_hash(cliente.documento, documento) si usas hash
        login_user(cliente)
        session['tipo_usuario'] = 'cliente'
        flash('Ingreso satisfactorio.', 'exito')  # Mensaje de exito
        return redirect(url_for('cliente.sistema'))  # Redirige a donde se muestra el modal
    else:
        flash('Correo o contraseña incorrectos.', 'error_sesion')
        return redirect(url_for('inicio') + '#loginCliente')


@cliente_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session['tipo_usuario'] = 'cliente'
    return redirect(url_for('inicio'))

#registro del cliente desde la pagina
@cliente_bp.route('/register', methods=['POST'])
def register():
    nombre = request.form.get('nombre', '').strip()
    documento = request.form.get('documento', '').strip()
    correo = request.form.get('correo', '').strip()
    telefono = request.form.get('telefono', '').strip()

    # Validaciones simples
    if not nombre  or not documento:
        flash("Todos los campos obligatorios deben estar completos.", "error")
        return redirect(url_for('inicio') + '#registroCliente')

    # Verificar si el documento ya existe
    from models.cliente_model import Cliente
    if Cliente.query.filter_by(documento=documento).first():
        flash("El número de documento ya está registrado.", "error")
        return redirect(url_for('inicio') + '#registroCliente')

    # Crear y guardar el cliente
    cliente = Cliente(nombre=nombre, documento=documento, correo=correo, telefono=telefono)
    cliente.save()

    flash("¡Registro exitoso! Ya puedes iniciar sesión.", "success")
    return redirect(url_for('inicio'))




@cliente_bp.route('/')
def index():
    clientes = Cliente.get_all()
    return cliente_view.list(clientes)

@cliente_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        documento = request.form.get('documento', '').strip()
        correo = request.form.get('correo', '').strip()
        telefono = request.form.get('telefono', '').strip()

        if not nombre or not documento or not correo:
            flash('Los campos nombre, documento y correo son obligatorios.', 'danger')
            return redirect(url_for('cliente.index'))

        cliente = Cliente(nombre=nombre, documento=documento, correo=correo, telefono=telefono)
        cliente.save()
        flash('Cliente registrado correctamente.', 'success')
        return redirect(url_for('cliente.index'))
    
    return cliente_view.create()



@cliente_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    cliente = Cliente.get_by_id(id)
    if not cliente:
        flash('Cliente no encontrado.', 'danger')
        return redirect(url_for('cliente.index'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        documento = request.form.get('documento', '').strip()
        correo = request.form.get('correo', '').strip()
        telefono = request.form.get('telefono', '').strip()

        if not nombre or not documento or not correo:
            flash('Los campos nombre, documento y correo son obligatorios.', 'danger')
            return cliente_view.edit(cliente)

        cliente.update(nombre=nombre, documento=documento, correo=correo, telefono=telefono)
        flash('Cliente actualizado correctamente.', 'success')
        return redirect(url_for('cliente.index'))
    
    return cliente_view.edit(cliente)

@cliente_bp.route('/delete/<int:id>')
def delete(id):
    cliente = Cliente.get_by_id(id)
    if cliente:
        cliente.delete()
        flash('Cliente eliminado correctamente.', 'success')
    else:
        flash('Cliente no encontrado.', 'danger')
    return redirect(url_for('cliente.index'))
