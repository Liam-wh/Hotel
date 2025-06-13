from flask import render_template
from flask_login import current_user

def sistema_admin():
    return render_template('usuarios/sistema_admin.html',usuario=current_user)

def sistema_resep():
    return render_template('usuarios/sistema_resep.html',usuario=current_user)

def list(clientes):
    return render_template('usuarios/index.html', clientes=clientes)

def create():
    return render_template('usuarios/create.html')

def edit(cliente):
    return render_template('usuarios/edit.html', cliente=cliente)