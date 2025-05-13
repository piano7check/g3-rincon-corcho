from flask import Flask, request, render_template, redirect, url_for, jsonify, abort, session
from registrar_usuarios import insertar_usuario
from buscar_usuarios import buscar_usuario_por_correo, buscar_usuario_por_id, correo_existe
from login_usuario import verificar_usuario
from editar_usuario import editar_usuario
from validaciones import es_nombre_valido, es_email_valido, es_password_seguro


app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  # Cambia esto por una clave secreta más segura

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

    # Validaciones
    if not es_nombre_valido(nombre):
        return render_template('formulario.html', error="Nombre inválido")
    if not es_email_valido(correo):
        return render_template('formulario.html', error="Correo inválido")
    if not es_password_seguro(password):
        return render_template('formulario.html', error="Contraseña insegura")

    # Verificar si el correo ya existe
    if correo_existe(correo):
        return render_template('formulario.html', error="El correo ya está registrado")

    # Intentar insertar usuario
    if insertar_usuario(nombre, correo, password):
        return redirect(url_for('bienvenida'))
    else:
        # Mostrar mensaje de error en la misma página
        return render_template('formulario.html', error="Hubo un error al insertar el usuario")

@app.route('/bienvenida')
def bienvenida():
    return render_template('rincon_del_corcho.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']

        # Validaciones
        if not es_email_valido(correo):
            return render_template('login.html', error="Correo inválido")
        if not password:
            return render_template('login.html', error="Contraseña requerida")

        ADMIN_TOKEN = "secreto123"  # Token para acceso de administrador
        modo_admin = request.form.get('modo_admin')  # None si no está marcado
        token = request.form.get('token', '')  # Vacío si no se ingresó

        # Verificar usuario
        usuario = verificar_usuario(correo, password)
        if usuario:
            session['id'] = usuario['id']

            # Si eligió modo administrador
            if modo_admin:
                if token == ADMIN_TOKEN:
                    return redirect(url_for('admin'))  # Redirige al panel admin
                else:
                    return render_template('login.html', error="Token de administrador incorrecto")
            else:
                return redirect(url_for('bienvenida'))  # Usuario normal

        else:
            return render_template('login.html', error="Correo o contraseña incorrectos")

    return render_template('login.html')



#Perfil
@app.route('/perfil')
def perfil():
    id_usuario = session.get('id')
    if not id_usuario:
        return redirect(url_for('login'))
    
    usuario = buscar_usuario_por_id(id_usuario)
    if not usuario:
        return "Usuario no encontrado", 404
    
    return render_template('perfil.html', usuario=usuario)
    
#editar usuario
@app.route('/editar', methods=['GET', 'POST'])
def editar_usuario_route():
    if request.method == 'POST':
        id_usuario = session.get('id')
        if not id_usuario:
            return redirect(url_for('login'))

        nuevo_nombre = request.form.get('nombre', '').strip()
        nuevo_correo = request.form.get('correo', '').strip()

        # Validaciones de nombre y correo
        if not es_nombre_valido(nuevo_nombre):
            return "Nombre inválido", 400
        if not es_email_valido(nuevo_correo):
            return "Correo inválido", 400

        # Actualizar usuario segun el usuario logueado
        if editar_usuario(id_usuario, nuevo_nombre, nuevo_correo):
            return redirect(url_for('bienvenida'))
        else:
            return "Error al editar el usuario", 400

    return render_template('editar_usuario.html')


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

