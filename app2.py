from flask import Flask, request, render_template, redirect, url_for, jsonify, abort, session
from flasgger import Swagger, swag_from

from registrar_usuarios import insertar_usuario
from login_usuario import verificar_usuario
from buscar_usuarios import buscar_usuario_por_correo, buscar_usuario_por_id
from editar_usuario import editar_usuario

app = Flask(__name__)
app.secret_key = 'clave_super_secreta_123'  # Reemplaza por una clave más segura en producción
swagger = Swagger(app)

@app.route('/')
def index():
    return render_template('formulario.html')


@app.route('/insertar', methods=['POST'])
@swag_from({
    'tags': ['Usuarios'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nombre': {'type': 'string'},
                    'correo': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['nombre', 'correo', 'password']
            }
        }
    ],
    'responses': {
        200: {'description': 'Usuario insertado correctamente o redirigido'},
        400: {'description': 'Error de validación o fallo al insertar'}
    }
})
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


@app.route('/buscar/<correo>', methods=['GET'])
@swag_from({
    'tags': ['Usuarios'],
    'parameters': [
        {
            'name': 'correo',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Correo del usuario a buscar'
        }
    ],
    'responses': {
        200: {'description': 'Usuario encontrado'},
        404: {'description': 'Usuario no encontrado'}
    }
})
def buscar_por_correo(correo):
    usuario = buscar_usuario_por_correo(correo)
    if usuario:
        return jsonify(usuario)
    else:
        abort(404, description="Usuario no encontrado")


@app.route('/usuario/<int:id>', methods=['GET'])
@swag_from({
    'tags': ['Usuarios'],
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del usuario a buscar'
        }
    ],
    'responses': {
        200: {'description': 'Usuario encontrado'},
        404: {'description': 'Usuario no encontrado'}
    }
})
def buscar_por_id(id):
    usuario = buscar_usuario_por_id(id)
    if usuario:
        return jsonify(usuario)
    else:
        abort(404, description="Usuario no encontrado")


@app.route('/login', methods=['GET', 'POST'])
@swag_from({
    'tags': ['Usuarios'],
    'parameters': [
        {
            'name': 'correo',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Correo del usuario'
        },
        {
            'name': 'password',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Contraseña del usuario'
        }
    ],
    'responses': {
        200: {'description': 'Login exitoso'},
        401: {'description': 'Credenciales incorrectas'}
    }
})
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']
        usuario = verificar_usuario(correo, password)
        if usuario:
            session['id'] = usuario['id']
            return redirect(url_for('bienvenida'))
        else:
            return "Correo o contraseña incorrectos", 401
    return render_template('login.html')


@app.route('/perfil', methods=['GET'])
@swag_from({
    'tags': ['Usuarios'],
    'responses': {
        200: {'description': 'Perfil mostrado correctamente'},
        401: {'description': 'No ha iniciado sesión'}
    }
})
def perfil():
    id_usuario = session.get('id')
    if not id_usuario:
        return redirect(url_for('login'))

    usuario = buscar_usuario_por_id(id_usuario)
    if not usuario:
        return "Usuario no encontrado", 404

    return render_template('perfil.html', usuario=usuario)


@app.route('/editar', methods=['GET', 'POST'])
@swag_from({
    'tags': ['Usuarios'],
    'parameters': [
        {
            'name': 'nombre',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Nuevo nombre del usuario'
        },
        {
            'name': 'correo',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Nuevo correo del usuario'
        }
    ],
    'responses': {
        200: {'description': 'Usuario editado correctamente'},
        400: {'description': 'Error al editar el usuario'}
    }
})
def editar_usuario_route():
    if request.method == 'POST':
        id_usuario = session.get('id')
        nuevo_nombre = request.form['nombre']
        nuevo_correo = request.form['correo']

        if editar_usuario(id_usuario, nuevo_nombre, nuevo_correo):
            return redirect(url_for('bienvenida'))
        else:
            return "Error al editar el usuario", 400
    return render_template('editar_usuario.html')


@app.route('/logout')
@swag_from({
    'tags': ['Usuarios'],
    'responses': {
        200: {'description': 'Sesión cerrada correctamente'}
    }
})
def logout():
    session.pop('id', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
