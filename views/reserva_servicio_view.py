from flask import render_template
from flask_login import current_user

def list(reservas_servicios, reservas, servicios):
    return render_template(
        "reserva_servicios/index.html",
        reservas_servicios=reservas_servicios,
        reservas=reservas,
        servicios=servicios,
        usuario=current_user
    )
