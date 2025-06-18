from flask import render_template
from flask_login import current_user

def sistema():
    return render_template('sistema.html',cliente=current_user)

def list(clientes):
    return render_template('clientes/index.html', clientes=clientes,usuario=current_user)
