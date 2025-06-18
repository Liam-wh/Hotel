from flask import render_template
from flask_login import current_user


def list(habitaciones):
    return render_template('habitaciones/index.html', habitaciones=habitaciones,usuario=current_user)

