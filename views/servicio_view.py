from flask import render_template
from flask_login import current_user


def list(servicios):
    return render_template('servicios/index.html', servicios=servicios,usuario=current_user)
