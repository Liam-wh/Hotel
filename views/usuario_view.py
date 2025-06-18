from flask import render_template
from flask_login import current_user


def sistema():
    return render_template('sistema.html',usuario=current_user)

def list(usuarios):
    return render_template('usuarios/index.html', usuarios=usuarios,usuario=current_user)

def create():
    return render_template('usuarios/create.html', usuario=current_user)

def edit(usuario):
    return render_template('usuarios/edit.html', usuario=usuario)