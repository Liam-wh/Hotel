from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/bienvenido')
def bienvenido():
    return render_template('pagina/index.html')

@app.route('/quienes_somos')
def quienes_somos():
    return render_template('pagina/quienes_somos.html')

@app.route('/servicios')
def servicios():
    return render_template('pagina/servicios.html')

@app.route('/noticias')
def noticias():
    return render_template('pagina/noticias.html')

@app.route('/contacto')
def contacto():
    return render_template('pagina/contacto.html')


if __name__ == '__main__':
    app.run(debug=True)
    