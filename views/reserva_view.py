from flask import render_template
from flask_login import current_user


def list(reservas,clientes,habitaciones):
    return render_template("reservas/index.html", reservas=reservas,clientes=clientes,habitaciones=habitaciones)

def create(clientes, habitaciones, fechas_ocupadas):
    return render_template("reservas/create.html", clientes=clientes, habitaciones=habitaciones, fechas_ocupadas=fechas_ocupadas, usuario=current_user )



