from flask import request, redirect, url_for, Blueprint, flash, jsonify, make_response, render_template, current_app
from models.reserva_model import Reserva
from models.cliente_model import Cliente
from models.habitacion_model import Habitacion
from views import reserva_view
from datetime import datetime, date
from flask_login import login_required
from collections import defaultdict
import pdfkit  # Para convertir HTML a PDF
from sqlalchemy import extract
from datetime import date, datetime, timedelta
import os

reserva_bp = Blueprint('reserva', __name__, url_prefix='/reservas')

from flask_login import current_user

@reserva_bp.route('/')
@login_required
def index():
    Reserva.actualizar_estados()
    habitaciones = Habitacion.get_all()

    if hasattr(current_user, 'rol'):  # Usuario interno
        reservas = Reserva.get_all()
    else:  # Cliente
        reservas = Reserva.query.filter_by(cliente_id=current_user.id).all()

    clientes = Cliente.get_all()
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
        # Validar que la habitación no esté ocupada en ese rango
        habitacion_reservas = Reserva.query.filter_by(habitacion_id=habitacion_id).all()

        for r in habitacion_reservas:
            if r.estado in ['ACTIVA', 'RESERVADA']:
                if (fecha_entrada < r.fecha_salida and fecha_salida > r.fecha_entrada):
                    flash('⚠️ HABITACIÓN OCUPADA EN ESA FECHA.', 'danger')
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
    # Construir fechas ocupadas
    fechas_ocupadas = defaultdict(list)
    for hab in habitaciones:
        for res in hab.reservas:
            fechas_ocupadas[hab.id].append({
                'inicio': res.fecha_entrada.isoformat(),
                'fin': res.fecha_salida.isoformat(),
                'estado': res.estado
            })

    return reserva_view.create(clientes, habitaciones, fechas_ocupadas)


@reserva_bp.route('/delete/<int:id>')
def delete(id):
    reserva = Reserva.get_by_id(id)
    if reserva:
        reserva.delete()
        flash('Reserva eliminada correctamente.', 'success')
    else:
        flash('La reserva no fue encontrada.', 'danger')
    return redirect(url_for('reserva.index'))



@reserva_bp.route('/cancelar/<int:id>')
@login_required
def cancelar(id):
    reserva = Reserva.get_by_id(id)
    if reserva and reserva.estado not in ['FINALIZADA', 'CANCELADA']:
        reserva.estado = 'CANCELADA'
        habitacion = Habitacion.get_by_id(reserva.habitacion_id)
        if habitacion:
            habitacion.estado = 'Disponible'
            habitacion.save()
        reserva.save()
        flash('Reserva cancelada correctamente.', 'success')
    else:
        flash('No se pudo cancelar la reserva.', 'danger')
    return redirect(url_for('reserva.index'))


@reserva_bp.route('/habitaciones_disponibles')
@login_required
def habitaciones_disponibles():
    entrada = request.args.get('fecha_entrada')
    salida = request.args.get('fecha_salida')

    if not entrada or not salida:
        return jsonify([])

    fecha_entrada = datetime.strptime(entrada, '%Y-%m-%d').date()
    fecha_salida = datetime.strptime(salida, '%Y-%m-%d').date()

    habitaciones = Habitacion.get_all()
    disponibles = []

    for hab in habitaciones:
        if hab.estado != 'Disponible':
            continue
        reservas = hab.reservas  

        solapada = any(
            not (res.fecha_salida <= fecha_entrada or res.fecha_entrada >= fecha_salida)
            for res in reservas
        )

        if not solapada:
            disponibles.append({
                "id": hab.id,
                "numero": hab.numero,
                "tipo": hab.tipo,
                "precio": hab.precio,
            })

    return jsonify(disponibles)


@reserva_bp.route('/<int:id>/pdf')
def generar_pdf(id):
    reserva = Reserva.get_by_id(id)
    if not reserva:
        return "Reserva no encontrada", 404

    servicios_reservados = reserva.res_servicios
    total_servicios = sum(rs.servicio.precio * rs.cantidad for rs in servicios_reservados)
    subtotal = reserva.total + total_servicios
    impuesto = subtotal * 0.13
    total_final = subtotal + impuesto

    # ✅ Ruta local para wkhtmltopdf
    modelo_path = os.path.join(current_app.root_path, 'static', 'images', 'modelo_mini.jpg')
    modelo_url = 'file://' + modelo_path

    html = render_template(
        'pdf/reserva_pdf.html',
        reserva=reserva,
        servicios=servicios_reservados,
        total_servicios=total_servicios,
        subtotal=subtotal,
        impuesto=impuesto,
        total_final=total_final,
        modelo_url=modelo_url
    )

    options = {
        'page-size': 'Letter',
        'margin-top': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
        'margin-right': '0mm',
        'encoding': "UTF-8",
        'enable-local-file-access': '',  # ✅ obligatorio para usar imágenes locales
        'print-media-type': '',          # ✅ útil si usas estilos @media print
    }

    pdf = pdfkit.from_string(html, False, options=options)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=Reserva_{reserva.id}_{reserva.cliente.nombre}.pdf'

    return response



@reserva_bp.route('/filtrar_fecha', methods=['GET'])
@login_required
def filtrar_por_fecha():
    fecha_str = request.args.get('fecha')
    if not fecha_str:
        flash("Debe proporcionar una fecha válida.", "warning")
        return redirect(url_for('reserva.index'))

    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        flash("Formato de fecha incorrecto.", "warning")
        return redirect(url_for('reserva.index'))

    reservas = Reserva.query.filter_by(fecha_entrada=fecha).all()
    clientes = Cliente.get_all()
    habitaciones = Habitacion.get_all()
    return reserva_view.list(reservas, clientes, habitaciones)




@reserva_bp.route('/reporte/pdf/rango', methods=['GET', 'POST'])
@login_required
def reporte_pdf_rango():
    if request.method == 'POST':
        mes_inicio = request.form.get('mes_inicio')
        mes_fin = request.form.get('mes_fin')

        if not mes_inicio or not mes_fin:
            flash("Debe ingresar ambos meses.", "warning")
            return redirect(url_for('reserva.index'))

        try:
            fecha_inicio = datetime.strptime(mes_inicio, "%Y-%m").date().replace(day=1)
            año_fin, mes_fin_num = map(int, mes_fin.split('-'))
            if mes_fin_num == 12:
                fecha_fin = date(año_fin + 1, 1, 1) - timedelta(days=1)
            else:
                fecha_fin = date(año_fin, mes_fin_num + 1, 1) - timedelta(days=1)
        except Exception:
            flash("Formato de mes inválido.", "danger")
            return redirect(url_for('reserva.index'))

        reservas = Reserva.query.filter(
            Reserva.fecha_entrada <= fecha_fin,
            Reserva.fecha_salida >= fecha_inicio
        ).all()

        # ✅ Usar ruta local absoluta para la imagen
        modelo_path = os.path.join(current_app.root_path, 'static', 'images', 'modelo_mini.jpg')
        modelo_url = 'file://' + modelo_path

        html = render_template(
            'pdf/reservas_rango_pdf.html',
            reservas=reservas,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            modelo_url=modelo_url
        )

        pdf = pdfkit.from_string(html, False, options={
            'enable-local-file-access': '',
            'page-size': 'Letter',
            'margin-top': '0mm',
            'margin-bottom': '0mm',
            'margin-left': '0mm',
            'margin-right': '0mm',
            'encoding': "UTF-8",
            'print-media-type': '',  # útil para imprimir estilos de fondo
        })

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = (
            f'inline; filename=Reporte_Reservas_{mes_inicio}_a_{mes_fin}.pdf'
        )

        return response

    return redirect(url_for('reserva.index'))

