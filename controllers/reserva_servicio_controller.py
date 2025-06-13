from flask import request, redirect, url_for, Blueprint, flash
from models.reserva_servicio_model import ReservaServicio
from views import reserva_servicio_view

reserva_servicio_bp = Blueprint('reserva_servicio', __name__, url_prefix='/reserva_servicios')

@reserva_servicio_bp.route('/')
def index():
    # Lista todas las asociaciones reserva-servicio
    registros = ReservaServicio.get_all()
    return reserva_servicio_view.list(registros)

@reserva_servicio_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        reserva_id = request.form.get('reserva_id', '').strip()
        servicio_id = request.form.get('servicio_id', '').strip()
        cantidad = request.form.get('cantidad', '').strip()

        if not reserva_id or not servicio_id:
            flash('Reserva y servicio son obligatorios.', 'error')
            return reserva_servicio_view.create()

        try:
            cantidad_val = int(cantidad) if cantidad else 1
        except ValueError:
            flash('Cantidad debe ser un número entero.', 'error')
            return reserva_servicio_view.create()

        registro = ReservaServicio(reserva_id=reserva_id, servicio_id=servicio_id, cantidad=cantidad_val)
        registro.save()
        flash('Servicio agregado a la reserva correctamente.', 'success')
        return redirect(url_for('reserva_servicio.index'))

    return reserva_servicio_view.create()

@reserva_servicio_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    registro = ReservaServicio.get_by_id(id)
    if not registro:
        flash('Registro no encontrado.', 'error')
        return redirect(url_for('reserva_servicio.index'))

    if request.method == 'POST':
        cantidad = request.form.get('cantidad', '').strip()

        try:
            cantidad_val = int(cantidad) if cantidad else registro.cantidad
        except ValueError:
            flash('Cantidad debe ser un número entero.', 'error')
            return reserva_servicio_view.edit(registro)

        registro.update(cantidad=cantidad_val)
        flash('Cantidad actualizada correctamente.', 'success')
        return redirect(url_for('reserva_servicio.index'))

    return reserva_servicio_view.edit(registro)

@reserva_servicio_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    registro = ReservaServicio.get_by_id(id)
    if registro:
        registro.delete()
        flash('Registro eliminado correctamente.', 'success')
    else:
        flash('Registro no encontrado.', 'error')
    return redirect(url_for('reserva_servicio.index'))
