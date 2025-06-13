from flask import render_template
from flask_login import current_user

def sistema():
    return render_template('clientes/sistema.html',cliente=current_user)

def list(clientes):
    return render_template('clientes/index.html', clientes=clientes)

def create():
    return render_template('clientes/create.html')

def edit(cliente):
    return render_template('clientes/edit.html', cliente=cliente)