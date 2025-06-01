from flask import Flask, request, render_template, redirect, url_for, jsonify, abort, session, flash
from werkzeug.utils import secure_filename
import os
import uuid
from registrar_usuarios import insertar_usuario
from buscar_usuarios import buscar_usuario_por_correo, buscar_usuario_por_id, correo_existe
from login_usuario import verificar_usuario
from editar_usuario import editar_usuario
from validaciones import es_nombre_valido, es_email_valido, es_password_seguro
from obtener_usuarios import obtener_todos_los_usuarios
from eliminar_usuario import eliminar_usuario_por_id
from carpetas_usuario import obtener_carpetas_usuario


app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  # Cambia esto por una clave secreta más segura

@app.route('/')
def index():
    return render_template('formulario.html')

@app.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    usuarios = obtener_todos_los_usuarios()
    return jsonify(usuarios)

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

@app.route('/logout')
def logout():
    session.clear()  # Limpia la sesión del usuario
    return redirect(url_for('login'))  # Redirige al login o index


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
    carpetas = obtener_carpetas_usuario(id_usuario)
    if not usuario:
        return "Usuario no encontrado", 404
    
    return render_template('perfil.html', usuario=usuario)
    
#editar usuario
@app.route('/editar', methods=['GET', 'POST'])
def editar_usuario_route():
    id_usuario = session.get('id')
    if not id_usuario:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip()
        password = request.form.get('password', '').strip()
        imagen = request.files.get('foto')

        # Validaciones
        if not es_nombre_valido(nombre):
            return render_template('editar_usuario.html', usuario=buscar_usuario_por_id(id_usuario), error="Nombre inválido")
        if not es_email_valido(correo):
            return render_template('editar_usuario.html', usuario=buscar_usuario_por_id(id_usuario), error="Correo inválido")
        if password and not es_password_seguro(password):
            return render_template('editar_usuario.html', usuario=buscar_usuario_por_id(id_usuario), error="Contraseña insegura")

        nueva_foto = None
        if imagen and imagen.filename != "":
            filename = secure_filename(imagen.filename)
            ext = os.path.splitext(filename)[1]
            nueva_foto = f"{uuid.uuid4().hex}{ext}"
            ruta = os.path.join("static", "imagenes", "perfiles", nueva_foto)
            imagen.save(ruta)

        # Actualizar usuario
        from editar_usuario import editar_usuario
        if editar_usuario(id_usuario, nombre, correo, nueva_foto, password):
            flash("Datos actualizados correctamente.")
            return redirect(url_for('perfil'))
        else:
            return render_template('editar_usuario.html', usuario=buscar_usuario_por_id(id_usuario), error="Error al guardar los datos")

    usuario = buscar_usuario_por_id(id_usuario)
    return render_template('editar_usuario.html', usuario=usuario)

@app.route('/EliminarCuenta', methods=['POST'])
def eliminar_cuenta():
    id_usuario = session.get('id')
    if not id_usuario:
        return redirect(url_for('login'))

    if eliminar_usuario_por_id(id_usuario):
        session.pop('id', None)
        return redirect(url_for('index'))
    else:
        print(f"❌ Error al intentar eliminar al usuario con ID {id_usuario}")
        return "Error al eliminar la cuenta", 500

@app.route("/cambiar_foto", methods=["GET", "POST"])
def cambiar_foto():
    id_usuario = session.get('id')
    if not id_usuario:
        return redirect(url_for('login'))

    if request.method == "POST":
        imagen = request.files.get("foto")
        if imagen and imagen.filename != "":
            filename = secure_filename(imagen.filename)
            ext = os.path.splitext(filename)[1]
            nuevo_nombre = f"{uuid.uuid4().hex}{ext}"
            ruta_guardado = os.path.join("static", "imagenes", "perfiles", nuevo_nombre)
            imagen.save(ruta_guardado)

            # Recuperar nombre y correo actual del usuario
            usuario = buscar_usuario_por_id(id_usuario)
            nombre_actual = usuario['nombre']
            correo_actual = usuario['correo']

            # Usar editar_usuario con los datos actuales + nueva foto
            if editar_usuario(id_usuario, nombre_actual, correo_actual, nuevo_nombre):
                flash("Imagen actualizada correctamente.")
            else:
                flash("Hubo un error al actualizar la imagen.")

            return redirect(url_for("perfil"))

        flash("No se seleccionó ninguna imagen válida.")
        return redirect(url_for("cambiar_foto"))

    return render_template("cambiar_foto.html")

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
        
@app.route('/hola-backend', methods=['GET'])
def hola_backend():
    return jsonify({"mensaje": "Hola Mundo desde el Backend"}), 200

@app.route('/error-backend', methods=['GET'])
def error_backend():
    return jsonify({"mensaje": "Adiós Mundo - Error simulado"}), 400


if __name__ == '__main__':
    app.run(debug=True)

