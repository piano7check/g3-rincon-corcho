from flask import Flask, request, render_template, redirect, url_for
from registrar_usuarios import insertar_usuario

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('formulario.html')

@app.route('/insertar', methods=['POST'])
def insertar():
    if request.is_json:
        data = request.get_json()
        nombre = data.get('nombre')
        correo = data.get('correo')
        password = data.get('password')
    else:
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']

    if insertar_usuario(nombre, correo, password):
        return redirect(url_for('bienvenida'))
    else:
        return "Hubo un error al insertar el usuario"

@app.route('/bienvenida')
def bienvenida():
    return render_template('rincon_del_corcho.html')

if __name__ == '__main__':
    app.run(debug=True)

