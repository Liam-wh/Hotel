from flask import request, redirect, url_for, Blueprint, flash, make_response, render_template, current_app
from models.habitacion_model import Habitacion
from views import habitacion_view
from flask_login import login_required
import pdfkit
import os


habitacion_bp = Blueprint('habitacion', __name__, url_prefix='/habitaciones')

@habitacion_bp.route('/')
@login_required
def index():
    habitaciones = Habitacion.get_all()
    return habitacion_view.list(habitaciones)

@habitacion_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        numero = request.form.get('numero', '').strip()
        tipo = request.form.get('tipo', '').strip()
        precio = request.form.get('precio', '').strip()
        estado = "Disponible"
        if not numero or not tipo or not precio:
            flash('Número, tipo y precio son obligatorios.', 'error')
            return habitacion_view.create()

        try:
            precio = float(precio)
        except ValueError:
            flash('Precio debe ser un número válido.', 'error')
            return habitacion_view.create()

        habitacion = Habitacion(numero, tipo, precio, estado)
        habitacion.save()
        flash('Habitación creada correctamente.', 'success')
        return redirect(url_for('habitacion.index'))
    return habitacion_view.create()




@habitacion_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    habitacion = Habitacion.get_by_id(id)
    if not habitacion:
        flash('Habitación no encontrada.', 'error')
        return redirect(url_for('habitacion.index'))
    if request.method == 'POST':
        numero = request.form.get('numero', '').strip()
        tipo = request.form.get('tipo', '').strip()
        precio = request.form.get('precio', '').strip()
        estado = request.form.get('estado', '').strip()

        if not numero or not tipo or not precio:
            flash('Número, tipo y precio son obligatorios.', 'error')
            return habitacion_view.edit(habitacion)

        try:
            precio = float(precio)
        except ValueError:
            flash('Precio debe ser un número válido.', 'error')
            return habitacion_view.edit(habitacion)

        habitacion.update(numero=numero, tipo=tipo, precio=precio, estado=estado)
        flash('Habitación actualizada correctamente.', 'success')
        return redirect(url_for('habitacion.index'))
    return habitacion_view.edit(habitacion)

@habitacion_bp.route('/delete/<int:id>')
def delete(id):
    habitacion = Habitacion.get_by_id(id)
    if habitacion:
        habitacion.delete()
        flash('Habitación eliminada correctamente.', 'success')
    else:
        flash('Habitación no encontrada.', 'error')
    return redirect(url_for('habitacion.index'))


@habitacion_bp.route('/reporte/pdf')
@login_required
def reporte_pdf():
    habitaciones = Habitacion.get_all()

    # ✅ Ruta absoluta a la imagen local
    modelo_path = os.path.join(current_app.root_path, 'static', 'images', 'modelo_red.jpg')
    modelo_url = 'file://' + modelo_path

    html = render_template('pdf/habitaciones_pdf.html', habitaciones=habitaciones, modelo_url=modelo_url)

    options = {
        'enable-local-file-access': '',
        'page-size': 'Legal',
        'margin-top': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
        'margin-right': '0mm',
        'encoding': "UTF-8",
        'no-outline': None,
        'print-media-type': '',  # Muy importante para backgrounds
    }

    pdf = pdfkit.from_string(html, False, options=options)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=reporte_habitaciones.pdf'

    return response


