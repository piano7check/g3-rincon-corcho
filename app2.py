from flask import Flask, request, render_template, redirect, url_for
from registrar_usuarios import insertar_usuario
from flasgger import Swagger, swag_from

app = Flask(__name__)
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
        200: {
            'description': 'Usuario insertado correctamente o redirigido',
        },
        400: {
            'description': 'Error de validación o fallo al insertar'
        }
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

if __name__ == '__main__':
    app.run(debug=True)