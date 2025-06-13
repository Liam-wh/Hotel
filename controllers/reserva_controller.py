from flask import request, redirect, url_for, Blueprint, flash
from models.reserva_model import Reserva
from views import reserva_view

reserva_bp = Blueprint('reserva', __name__, url_prefix='/reservas')

@reserva_bp.route('/')
def index():
    reservas = Reserva.get_all()
    return reserva_view.list(reservas)

@reserva_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id', '').strip()
        habitacion_id = request.form.get('habitacion_id', '').strip()
        fecha_inicio = request.form.get('fecha_inicio', '').strip()
        fecha_fin = request.form.get('fecha_fin', '').strip()

        if not cliente_id or not habitacion_id or not fecha_inicio or not fecha_fin:
            flash('Todos los campos son obligatorios.', 'error')
            return reserva_view.create()

        reserva = Reserva(cliente_id, habitacion_id, fecha_inicio, fecha_fin)
        reserva.save()
        flash('Reserva creada correctamente.', 'success')
        return redirect(url_for('reserva.index'))
    return reserva_view.create()

@reserva_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    reserva = Reserva.get_by_id(id)
    if not reserva:
        flash('Reserva no encontrada.', 'error')
        return redirect(url_for('reserva.index'))
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id', '').strip()
        habitacion_id = request.form.get('habitacion_id', '').strip()
        fecha_inicio = request.form.get('fecha_inicio', '').strip()
        fecha_fin = request.form.get('fecha_fin', '').strip()

        if not cliente_id or not habitacion_id or not fecha_inicio or not fecha_fin:
            flash('Todos los campos son obligatorios.', 'error')
            return reserva_view.edit(reserva)

        reserva.update(cliente_id=cliente_id, habitacion_id=habitacion_id, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
        flash('Reserva actualizada correctamente.', 'success')
        return redirect(url_for('reserva.index'))
    return reserva_view.edit(reserva)

@reserva_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    reserva = Reserva.get_by_id(id)
    if reserva:
        reserva.delete()
        flash('Reserva eliminada correctamente.', 'success')
    else:
        flash('Reserva no encontrada.', 'error')
    return redirect(url_for('reserva.index'))
