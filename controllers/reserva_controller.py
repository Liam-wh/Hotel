from flask import request, redirect, url_for, Blueprint, flash
from models.reserva_model import Reserva
from models.cliente_model import Cliente
from models.habitacion_model import Habitacion
from views import reserva_view
from datetime import datetime, date
from flask_login import login_required

reserva_bp = Blueprint('reserva', __name__, url_prefix='/reservas')


@reserva_bp.route('/')
@login_required
def index():
    Reserva.actualizar_estados()  # actualiza estados antes de mostrar
    reservas = Reserva.get_all()
    clientes = Cliente.get_all()
    habitaciones = Habitacion.get_all()
    return reserva_view.list(reservas, clientes, habitaciones)


@reserva_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        habitacion_id = request.form['habitacion_id']
        usuario_id = request.form['usuario']

        fecha_entrada_str = request.form['fecha_entrada']
        fecha_salida_str = request.form['fecha_salida']
        total_raw = request.form.get('total', '').strip()

        # Validación inicial de fechas
        try:
            fecha_entrada = datetime.strptime(fecha_entrada_str, '%Y-%m-%d').date()
            fecha_salida = datetime.strptime(fecha_salida_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Formato de fecha inválido.', 'warning')
            return redirect(url_for('reserva.create'))

        # Verificar fechas
        if fecha_salida <= fecha_entrada:
            flash('La fecha de salida debe ser posterior a la de entrada.', 'warning')
            return redirect(url_for('reserva.create'))

        if fecha_entrada < date.today():
            flash('La fecha de entrada no puede ser anterior al día de hoy.', 'warning')
            return redirect(url_for('reserva.create'))

        # Validar total
        if not total_raw:
            flash('Debe calcularse el total antes de confirmar la reserva.', 'warning')
            return redirect(url_for('reserva.create'))

        try:
            total = float(total_raw)
            if total <= 0:
                raise ValueError
        except ValueError:
            flash('El total ingresado no es válido.', 'warning')
            return redirect(url_for('reserva.create'))

        # Guardar
        estado = "RESERVADA"
        reserva = Reserva(
            cliente_id=int(cliente_id),
            habitacion_id=int(habitacion_id),
            fecha_entrada=fecha_entrada,
            fecha_salida=fecha_salida,
            estado=estado,
            total=total,
            usuario_id=usuario_id
        )
        reserva.save()

        flash('Reserva creada correctamente.', 'success')
        return redirect(url_for('reserva.index'))

    clientes = Cliente.get_all()
    habitaciones = Habitacion.get_all()
    return reserva_view.create(clientes, habitaciones)




@reserva_bp.route('/delete/<int:id>')
def delete(id):
    reserva = Reserva.get_by_id(id)
    if reserva:
        reserva.delete()
        flash('Reserva eliminada correctamente.', 'success')
    else:
        flash('La reserva no fue encontrada.', 'danger')
    return redirect(url_for('reserva.index'))
