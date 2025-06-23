from flask import request, redirect, url_for, Blueprint, flash, render_template, make_response
from models.servicio_model import Servicio
from views import servicio_view
from flask_login import login_required
import pdfkit

servicio_bp = Blueprint('servicio', __name__, url_prefix='/servicios')

@servicio_bp.route('/')
@login_required
def index():
    servicios = Servicio.get_all()
    return servicio_view.list(servicios)

@servicio_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        precio = request.form.get('precio', '').strip()

        if not nombre or not precio:
            flash('Nombre y precio son obligatorios.', 'error')
            return servicio_view.create()

        try:
            precio = float(precio)
        except ValueError:
            flash('Precio debe ser un número válido.', 'error')
            return servicio_view.create()

        servicio = Servicio(nombre, descripcion, precio)
        servicio.save()
        flash('Servicio creado correctamente.', 'success')
        return redirect(url_for('servicio.index'))
    return servicio_view.create()

@servicio_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    servicio = Servicio.get_by_id(id)
    if not servicio:
        flash('Servicio no encontrado.', 'error')
        return redirect(url_for('servicio.index'))
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        precio = request.form.get('precio', '').strip()

        if not nombre or not precio:
            flash('Nombre y precio son obligatorios.', 'error')
            return servicio_view.edit(servicio)

        try:
            precio = float(precio)
        except ValueError:
            flash('Precio debe ser un número válido.', 'error')
            return servicio_view.edit(servicio)

        servicio.update(nombre=nombre, descripcion=descripcion, precio=precio)
        flash('Servicio actualizado correctamente.', 'success')
        return redirect(url_for('servicio.index'))
    return servicio_view.edit(servicio)

@servicio_bp.route('/delete/<int:id>')
def delete(id):
    servicio = Servicio.get_by_id(id)
    if servicio:
        servicio.delete()
        flash('Servicio eliminado correctamente.', 'success')
    else:
        flash('Servicio no encontrado.', 'error')
    return redirect(url_for('servicio.index'))



@servicio_bp.route('/reporte/pdf')
@login_required
def reporte_pdf():
    servicios = Servicio.get_all()
    modelo_url = request.host_url.rstrip('/') + url_for('static', filename='images/modelo_pdf.jpg')

    html = render_template('pdf/servicios_pdf.html', servicios=servicios, modelo_url=modelo_url)

    options = {
        'enable-local-file-access': '',
        'page-size': 'Letter',
        'margin-top': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
        'margin-right': '0mm',
        'encoding': "UTF-8",
        'no-outline': None,
    }

    pdf = pdfkit.from_string(html, False, options=options)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    # Mostrar inline en navegador (previa)
    response.headers['Content-Disposition'] = 'inline; filename=reporte_servicios.pdf'

    return response

