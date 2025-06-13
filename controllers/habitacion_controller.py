from flask import request, redirect, url_for, Blueprint, flash
from models.habitacion_model import Habitacion
from views import habitacion_view

habitacion_bp = Blueprint('habitacion', __name__, url_prefix='/habitaciones')

@habitacion_bp.route('/')
def index():
    habitaciones = Habitacion.get_all()
    return habitacion_view.list(habitaciones)

@habitacion_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        numero = request.form.get('numero', '').strip()
        tipo = request.form.get('tipo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        precio = request.form.get('precio', '').strip()

        if not numero or not tipo or not precio:
            flash('Número, tipo y precio son obligatorios.', 'error')
            return habitacion_view.create()

        try:
            precio = float(precio)
        except ValueError:
            flash('Precio debe ser un número válido.', 'error')
            return habitacion_view.create()

        habitacion = Habitacion(numero, tipo, descripcion, precio)
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
        descripcion = request.form.get('descripcion', '').strip()
        precio = request.form.get('precio', '').strip()

        if not numero or not tipo or not precio:
            flash('Número, tipo y precio son obligatorios.', 'error')
            return habitacion_view.edit(habitacion)

        try:
            precio = float(precio)
        except ValueError:
            flash('Precio debe ser un número válido.', 'error')
            return habitacion_view.edit(habitacion)

        habitacion.update(numero=numero, tipo=tipo, descripcion=descripcion, precio=precio)
        flash('Habitación actualizada correctamente.', 'success')
        return redirect(url_for('habitacion.index'))
    return habitacion_view.edit(habitacion)

@habitacion_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    habitacion = Habitacion.get_by_id(id)
    if habitacion:
        habitacion.delete()
        flash('Habitación eliminada correctamente.', 'success')
    else:
        flash('Habitación no encontrada.', 'error')
    return redirect(url_for('habitacion.index'))
