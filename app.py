from flask import Flask, request, render_template, redirect, url_for, jsonify, abort
from registrar_usuarios import insertar_usuario
from buscar_usuarios import buscar_usuario_por_correo, buscar_usuario_por_id


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

@app.route('/admin')
def admin():
    return render_template('admin.html')

#buscar usuario por correo
@app.route('/buscar/<correo>', methods=['GET'])
def buscar_por_correo(correo):
    usuario = buscar_usuario_por_correo(correo)
    if usuario:
        return jsonify(usuario)
    else:
        abort(404, description="Usuario no encontrado")

#buscar usuario por ID
@app.route('/usuario/<int:id>', methods=['GET'])
def buscar_por_id(id):
    usuario = buscar_usuario_por_id(id)
    if usuario:
        return jsonify(usuario)
    else:
        abort(404, description="Usuario no encontrado")


if __name__ == '__main__':
    app.run(debug=True)

