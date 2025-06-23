from flask import request, redirect, url_for, Blueprint, flash, session, render_template, make_response
from flask_login import login_user, logout_user, login_required, current_user
from models.cliente_model import Cliente
from views import cliente_view
import pdfkit

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

@cliente_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def actualizar_perfil():
    if not hasattr(current_user, 'documento'):  # Asegura que sea cliente
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('inicio'))

    cliente = current_user

    if request.method == 'POST':
        cliente.nombre = request.form['nombre']
        cliente.documento = request.form['documento']
        cliente.correo = request.form['correo']
        cliente.telefono = request.form['telefono']
        cliente.save()
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('cliente.actualizar_perfil'))

    return render_template('clientes/perfil.html', cliente=cliente)


@cliente_bp.route('/buscar', methods=['GET'])
@login_required
def buscar_documento():
    documento = request.args.get('documento')
    cliente = Cliente.query.filter_by(documento=documento).first()
    if cliente:
        return render_template('clientes/index.html', clientes=[cliente])  # lista con un solo cliente
    else:
        flash('Cliente no encontrado.', 'warning')
        return redirect(url_for('cliente.index'))



@cliente_bp.route('/reporte/pdf')
@login_required
def reporte_pdf():
    clientes = Cliente.get_all()
    modelo_url = request.host_url.rstrip('/') + url_for('static', filename='images/modelo_pdf.jpg')

    html = render_template('pdf/clientes_pdf.html', clientes=clientes, modelo_url=modelo_url)

    options = {
        'enable-local-file-access': '',
        'page-size': 'Letter',
        'encoding': "UTF-8",
        'margin-top': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
        'margin-right': '0mm',
        'no-images': '',
        'no-outline': None
    }

    pdf = pdfkit.from_string(html, False, options=options)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=reporte_clientes.pdf'

    return response


