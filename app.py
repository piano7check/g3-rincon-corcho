from flask import Flask, request, render_template, redirect, url_for, jsonify, abort, session, flash, send_file
import bcrypt
from werkzeug.utils import secure_filename
import os
import uuid
import io  # Importar io para manejar datos binarios como archivos
import pyodbc # Importar pyodbc para la conexión a SQL Server

# Importaciones de tus módulos existentes
from registrar_usuarios import insertar_usuario
from buscar_usuarios import buscar_usuario_por_correo, buscar_usuario_por_id, correo_existe, buscar_usuario_por_nombre
from login_usuario import verificar_usuario # Asumo que esta es la función que verifica en la DB
from editar_usuario import editar_usuario
from validaciones import es_nombre_valido, es_email_valido, es_password_seguro
from obtener_usuarios import obtener_todos_los_usuarios
from eliminar_usuario import eliminar_usuario_por_id
from carpetas_usuario import obtener_carpetas_usuario
from conexion_database import get_connection # Asumo que esta función existe en tu modulo y maneja la conexión a la DB
from comentarios import agregar_comentario, obtener_comentarios, eliminar_comentario, editar_comentario
from eliminar_documento import eliminar_documento

app = Flask(__name__)
# Puedes generar una con: os.urandom(24).hex()
app.secret_key = 'secreto123' 

# --- Funciones de Ayuda para la Base de Datos ---

def obtener_todas_las_materias():
    """Obtiene todas las materias con su id, nombre, semestre y cantidad de documentos."""
    conn = None
    materias = []
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.id_materia, m.nombre_materia, m.semestre, 
                       COUNT(d.id_documento) as cantidad_documentos
                FROM materias m
                LEFT JOIN documentos d ON m.id_materia = d.id_materia
                GROUP BY m.id_materia, m.nombre_materia, m.semestre
                ORDER BY m.nombre_materia, m.semestre;
            """)
            materias = cursor.fetchall() # [(id, nombre, semestre, cantidad_documentos), ...]
    except Exception as e:
        print(f"Error al obtener las materias: {e}")
    finally:
        if conn:
            conn.close()
    return materias

# --- Rutas de la Aplicación ---

@app.route('/')
def index():
    """
    Ruta raíz que redirige según si el usuario está logueado o no.
    Si hay sesión, va a 'bienvenida' (o 'perfil'), si no, a 'login'.
    """
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Maneja el inicio de sesión de los usuarios.
    - GET: Muestra el formulario de login.
    - POST: Procesa los datos del formulario (correo y contraseña).
    """
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']
        modo_admin = request.form.get('modo_admin')
        token = request.form.get('token', '').strip()

        # Verifica las credenciales del usuario usando tu función `verificar_usuario`
        usuario = verificar_usuario(correo, password)
        if usuario:
            # Si el usuario solicita modo admin y el token es correcto
            if modo_admin and token == 'secreto123':
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE usuarios SET rol = 'admin' WHERE correo = ?", correo)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    usuario['rol'] = 'admin'  # Actualiza el dict local también
                except Exception as e:
                    print("Error actualizando rol a admin:", e)
                    flash("No se pudo actualizar el rol a administrador.", "error")
                    return render_template('login.html')
            session['id'] = usuario['id']
            session['rol'] = usuario['rol']
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for('bienvenida'))
        else:
            flash("Correo o contraseña incorrectos", "error")
            return render_template('login.html')
    
    # Si la solicitud es GET, simplemente renderiza la plantilla de login
    return render_template('login.html')

# NUEVA RUTA: Para el botón de "Registrarme"
@app.route('/registro')
def registro():
    """Renderiza la página de registro de usuarios (formulario.html)."""
    return render_template('formulario.html') 

@app.route('/insertar', methods=['POST'])
def insertar():
    """
    Maneja el registro de nuevos usuarios.
    Asume que 'formulario.html' es la página de registro.
    """
    if request.is_json: # Soporte para registro desde API (si aplica)
        data = request.get_json()
        nombre = data.get('nombre')
        correo = data.get('correo')
        password = data.get('password')
    else: # Registro desde formulario HTML
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']

    # Validaciones de los datos de registro
    if not es_nombre_valido(nombre):
        flash("Nombre inválido. Solo se permiten letras y espacios.", "error")
        return render_template('formulario.html')
    # Validación de nombre duplicado
    if buscar_usuario_por_nombre(nombre):
        flash("El nombre ya está registrado. Por favor, utiliza otro.", "error")
        return render_template('formulario.html')
    if not es_email_valido(correo):
        flash("Correo inválido.", "error")
        return render_template('formulario.html')
    if not es_password_seguro(password):
        flash("Contraseña insegura. Debe tener al menos 8 caracteres, mayúscula, minúscula, número y símbolo.", "error")
        return render_template('formulario.html')

    # Verifica si el correo ya existe en la base de datos
    if correo_existe(correo):
        flash("El correo ya está registrado. Por favor, utiliza otro o inicia sesión.", "error")
        return render_template('formulario.html')

    # Intenta insertar el nuevo usuario
    if insertar_usuario(nombre, correo, password):
        flash("Registro exitoso. Por favor, inicia sesión.", "success")
        return redirect(url_for('login')) # Redirige al login después de registrarse
    else:
        flash("Hubo un error al insertar el usuario. Por favor, inténtalo de nuevo.", "error")
        return render_template('formulario.html')

@app.route('/bienvenida')
def bienvenida():
    """
    Página principal después del login, muestra documentos y materias.
    Requiere que el usuario esté logueado.
    """
    if 'id' not in session:
        flash("Debes iniciar sesión para acceder a esta página.", "info") 
        return redirect(url_for('login'))
    
    conn = None
    documentos = []
    # Obtiene todas las materias para mostrarlas en las tarjetas y el modal de subida
    materias = obtener_todas_las_materias() 

    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            # Consulta para obtener los documentos con información del usuario y materia
            cursor.execute("""
                SELECT d.id_documento, d.nombre_documento, d.fecha_subida,
                u.nombre AS nombre_usuario, m.nombre_materia, m.semestre,
                d.id_usuario  -- <- agregado al final
                FROM documentos d
                INNER JOIN usuarios u ON d.id_usuario = u.id_usuario
                INNER JOIN materias m ON d.id_materia = m.id_materia
                ORDER BY d.fecha_subida DESC;
            """)
            documentos_raw = cursor.fetchall() # Obtener resultados como tuplas
            
            # Convierte las tuplas a diccionarios para facilitar el acceso en la plantilla Jinja
            documentos = []
            for doc in documentos_raw:
                documentos.append({
                    'id_documento': doc[0],
                    'nombre_documento': doc[1],
                    'fecha_subida': doc[2],
                    'nombre_usuario': doc[3],
                    'nombre_materia': doc[4],
                    'semestre': doc[5],
                    'id_usuario': doc[6]

                })

    except Exception as e:
        print(f"Error al obtener documentos: {e}")
        # flash("Error al cargar los documentos.", "error") # Eliminado para esta ruta
    finally:
        if conn:
            conn.close()

    # Pasa los documentos y las materias a la plantilla
    return render_template('rincon_del_corcho.html', materias=materias, documentos=documentos)

# Ruta para ver los documentos de una materia específica
@app.route('/materia/<int:id_materia>')
def documentos_materia(id_materia):
    if 'id' not in session:
        flash('Debes iniciar sesión para ver los documentos de la materia.', 'warning')
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre_materia, semestre FROM materias WHERE id_materia = ?", id_materia)
    materia = cursor.fetchone()

    cursor.execute("""
        SELECT d.id_documento, d.nombre_documento, d.fecha_subida, d.id_usuario, u.nombre AS nombre_usuario
        FROM documentos d
        JOIN usuarios u ON d.id_usuario = u.id_usuario
        WHERE d.id_materia = ?
        ORDER BY d.fecha_subida DESC
    """, id_materia)
    documentos = cursor.fetchall()
    conn.close()

    return render_template('documentos_materia.html', materia=materia, documentos=documentos)


@app.route('/admin')
def admin():
    if 'rol' not in session or session['rol'] != 'admin':
        flash("Acceso denegado.", "error")
        return redirect(url_for('bienvenida'))
    # Puedes pasar aquí datos de administración si lo deseas
    return render_template('admin.html')

@app.route('/logout')
def logout():
    """
    Cierra la sesión del usuario.
    """
    session.clear()  # Limpia todos los datos de la sesión
    flash("Has cerrado sesión correctamente.", "info") 
    return redirect(url_for('login'))  # Redirige a la página de login

@app.route('/perfil')
def perfil():
    """
    Muestra la página de perfil del usuario logueado.
    """
    id_usuario = session.get('id')
    if not id_usuario:
        flash("Debes iniciar sesión para ver tu perfil.", "info")
        return redirect(url_for('login'))
    
    usuario = buscar_usuario_por_id(id_usuario)
    carpetas = obtener_carpetas_usuario(id_usuario)
    if not usuario:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for('logout')) # Si el usuario no existe, cierra la sesión

    return render_template('perfil.html', usuario=usuario, carpetas=carpetas)
    
@app.route('/editar', methods=['GET', 'POST'])
def editar_usuario_route():
    """
    Permite al usuario editar su información de perfil.
    """
    id_usuario = session.get('id')
    if not id_usuario:
        flash("Debes iniciar sesión para editar tu perfil.", "info")
        return redirect(url_for('login'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip()
        password = request.form.get('password', '').strip() # Nueva contraseña, si se proporciona

        usuario_actual = buscar_usuario_por_id(id_usuario)
        if not usuario_actual:
            flash("Error: Usuario no encontrado para edición.", "error")
            return redirect(url_for('logout'))

        nombre_actual_db = usuario_actual['nombre']
        correo_actual_db = usuario_actual['correo']
        foto_actual_db = usuario_actual['foto'] # Asumo que tu tabla 'usuarios' tiene una columna 'foto'

        # Usa los valores del formulario si se proporcionan, de lo contrario, usa los de la DB
        nombre_a_actualizar = nombre if nombre else nombre_actual_db
        correo_a_actualizar = correo if correo else correo_actual_db

        # Validaciones para los datos a actualizar
        if not es_nombre_valido(nombre_a_actualizar):
            flash("Nombre inválido.", "error")
            return render_template('editar_usuario.html', usuario=buscar_usuario_por_id(id_usuario))
        if not es_email_valido(correo_a_actualizar):
            flash("Correo inválido.", "error")
            return render_template('editar_usuario.html', usuario=buscar_usuario_por_id(id_usuario))
        # Solo valida la contraseña si el usuario ha introducido una nueva
        if password and not es_password_seguro(password):
            flash("Contraseña insegura. Debe tener al menos 8 caracteres, mayúscula, minúscula, número y símbolo.", "error")
            return render_template('editar_usuario.html', usuario=buscar_usuario_por_id(id_usuario))

        # Lógica para la foto de perfil:
        nueva_foto_nombre_archivo = foto_actual_db # Por defecto, mantiene la foto actual
        imagen_file = request.files.get('foto_perfil') # Nombre del input type="file" en tu formulario HTML
        
        if imagen_file and imagen_file.filename != "":
            filename = secure_filename(imagen_file.filename)
            ext = os.path.splitext(filename)[1] # Obtiene la extensión del archivo
            nuevo_nombre_uuid = f"{uuid.uuid4().hex}{ext}" # Genera un nombre único
            ruta_guardado = os.path.join(app.static_folder, "imagenes", "perfiles", nuevo_nombre_uuid)
            try:
                os.makedirs(os.path.dirname(ruta_guardado), exist_ok=True) # Crea el directorio si no existe
                imagen_file.save(ruta_guardado)
                nueva_foto_nombre_archivo = nuevo_nombre_uuid # Actualiza el nombre para guardar en la DB
                # Opcional: Eliminar la foto antigua para ahorrar espacio
                # if foto_actual_db and os.path.exists(os.path.join(app.static_folder, "imagenes", "perfiles", foto_actual_db)):
                #     os.remove(os.path.join(app.static_folder, "imagenes", "perfiles", foto_actual_db))
            except Exception as e:
                print(f"Error al guardar la nueva imagen de perfil: {e}")
                flash("Error al guardar la nueva imagen de perfil.", "error")
                return render_template('editar_usuario.html', usuario=usuario_actual)

        # Llama a la función `editar_usuario` de tu módulo `editar_usuario.py`
        # Pasa `None` para la contraseña si el campo estaba vacío, indicando que no se debe cambiar.
        if editar_usuario(id_usuario, nombre_a_actualizar, correo_a_actualizar, nueva_foto_nombre_archivo, password):
            flash("Datos actualizados correctamente.", "success")
            return redirect(url_for('perfil'))
        else:
            flash("Error al guardar los datos. Inténtalo de nuevo.", "error")
            return render_template('editar_usuario.html', usuario=buscar_usuario_por_id(id_usuario))

    # Si la solicitud es GET, renderiza la plantilla de edición con los datos actuales del usuario
    usuario = buscar_usuario_por_id(id_usuario)
    return render_template('editar_usuario.html', usuario=usuario)

@app.route('/EliminarCuenta', methods=['POST'])
def eliminar_cuenta():
    """
    Permite al usuario eliminar su propia cuenta.
    """
    id_usuario = session.get('id')
    if not id_usuario:
        flash("Debes iniciar sesión para eliminar tu cuenta.", "info")
        return redirect(url_for('login'))

    if eliminar_usuario_por_id(id_usuario): # Llama a tu función de eliminación
        session.pop('id', None) # Limpia la sesión del usuario
        flash("Tu cuenta ha sido eliminada correctamente.", "success")
        return redirect(url_for('index')) # Redirige al inicio o al login
    else:
        print(f"❌ Error al intentar eliminar al usuario con ID {id_usuario}")
        flash("Error al eliminar la cuenta. Por favor, inténtalo de nuevo.", "error")
        return "Error al eliminar la cuenta", 500 # Devuelve un error 500 si falla

@app.route("/cambiar_foto", methods=["GET", "POST"])
def cambiar_foto():
    """
    Ruta específica para cambiar solo la foto de perfil.
    """
    id_usuario = session.get('id')
    if not id_usuario:
        flash("Debes iniciar sesión para cambiar tu foto de perfil.", "info")
        return redirect(url_for('login'))

    if request.method == "POST":
        imagen = request.files.get("foto") # Nombre del input type="file"
        if imagen and imagen.filename != "":
            filename = secure_filename(imagen.filename)
            ext = os.path.splitext(filename)[1]
            nuevo_nombre = f"{uuid.uuid4().hex}{ext}" # Nombre de archivo único
            ruta_guardado = os.path.join(app.static_folder, "imagenes", "perfiles", nuevo_nombre)
            try:
                os.makedirs(os.path.dirname(ruta_guardado), exist_ok=True)
                imagen.save(ruta_guardado)
            except Exception as e:
                print(f"Error al guardar la imagen: {e}")
                flash("Error al guardar la nueva imagen.", "error")
                return redirect(url_for("cambiar_foto"))

            # Recuperar nombre y correo actual del usuario (ya que editar_usuario los requiere)
            usuario = buscar_usuario_por_id(id_usuario)
            if not usuario:
                flash("Usuario no encontrado para actualizar foto.", "error")
                return redirect(url_for('logout'))

            nombre_actual = usuario['nombre']
            correo_actual = usuario['correo']

            # Usa `editar_usuario` para actualizar solo el campo de la foto, pasando None para la contraseña
            if editar_usuario(id_usuario, nombre_actual, correo_actual, nuevo_nombre, None):
                flash("Imagen actualizada correctamente.", "success")
            else:
                flash("Hubo un error al actualizar la imagen.", "error")

            return redirect(url_for("perfil"))

        flash("No se seleccionó ninguna imagen válida.", "warning")
        return redirect(url_for("cambiar_foto"))

    return render_template("cambiar_foto.html")

@app.route('/buscar/<correo>', methods=['GET'])
def buscar_por_correo_api(correo):
    """API: Busca un usuario por correo electrónico."""
    usuario = buscar_usuario_por_correo(correo)
    if usuario:
        return jsonify(usuario)
    else:
        abort(404, description="Usuario no encontrado")

@app.route('/usuario/<int:id>', methods=['GET'])
def buscar_por_id_api(id):
    """API: Busca un usuario por ID."""
    usuario = buscar_usuario_por_id(id)
    if usuario:
        return jsonify(usuario)
    else:
        abort(404, description="Usuario no encontrado")
        
@app.route('/hola-backend', methods=['GET'])
def hola_backend():
    """Ruta de prueba simple."""
    return jsonify({"mensaje": "Hola Mundo desde el Backend"}), 200

@app.route('/error-backend', methods=['GET'])
def error_backend():
    """Ruta para simular un error."""
    return jsonify({"mensaje": "Adiós Mundo - Error simulado"}), 400

# --- Lógica de Subida y Descarga de Documentos ---
@app.route('/subir_documento', methods=['POST'])
def subir_documento():
    """
    Maneja la subida de documentos.
    Requiere nombre del documento, semestre, materia y el archivo PDF.
    """
    id_usuario = session.get('id')
    if not id_usuario:
        flash("Debes iniciar sesión para subir documentos.", "info")
        return redirect(url_for('login'))

    # Obtiene todos los datos del formulario
    nombre_documento_input = request.form.get('nombre_documento_input', '').strip()
    semestre_seleccionado = request.form.get('materia_semestre', '').strip()
    nombre_materia_seleccionada = request.form.get('materia_nombre', '').strip()

    # Validaciones de campos obligatorios
    if not nombre_documento_input:
        flash("El nombre del documento es obligatorio.", "warning")
        return redirect(url_for('bienvenida'))
    if not semestre_seleccionado:
        flash("Debe seleccionar un semestre para el documento.", "warning")
        return redirect(url_for('bienvenida'))
    if not nombre_materia_seleccionada:
        flash("Debe seleccionar una materia para el documento.", "warning")
        return redirect(url_for('bienvenida'))
    
    # Validaciones del archivo
    if 'documento_file' not in request.files:
        flash("No se seleccionó ningún archivo.", "warning")
        return redirect(url_for('bienvenida'))
    file = request.files['documento_file']
    if file.filename == '':
        flash("Nombre de archivo vacío. Por favor, selecciona un archivo.", "warning")
        return redirect(url_for('bienvenida'))

    conn = None
    try:
        conn = get_connection()
        if conn is None:
            flash("Error: No se pudo conectar a la base de datos para subir el archivo.", "error")
            return redirect(url_for('bienvenida'))

        cursor = conn.cursor()

        # 1. Obtener el id_materia a partir del nombre_materia Y semestre seleccionados
        cursor.execute("SELECT id_materia FROM materias WHERE nombre_materia = ? AND semestre = ?", 
                       nombre_materia_seleccionada, semestre_seleccionado)
        materia_row = cursor.fetchone()
        
        if not materia_row:
            flash(f"La combinación de materia '{nombre_materia_seleccionada}' y semestre '{semestre_seleccionado}' no existe en la base de datos.", "error")
            return redirect(url_for('bienvenida'))
        
        id_materia = materia_row[0] # Accedemos al id_materia desde la tupla

        # 2. Leer el contenido binario del archivo
        tipo_contenido = file.content_type
        datos_documento = file.read()

        # 3. Insertar el documento en la tabla 'Documentos'
        sql_insert = """
        INSERT INTO Documentos (nombre_documento, tipo_contenido, datos_documento, id_usuario, id_materia)
        VALUES (?, ?, ?, ?, ?);
        """
        cursor.execute(sql_insert, nombre_documento_input, tipo_contenido, pyodbc.Binary(datos_documento), id_usuario, id_materia)
        conn.commit()
        print(f"Documento '{nombre_documento_input}' subido exitosamente a la DB por usuario {id_usuario}.")
        flash(f"Documento '{nombre_documento_input}' subido exitosamente. La página se ha actualizado.", "success")
        return redirect(url_for('bienvenida')) # Redirige a bienvenida para recargar la lista de documentos
    except Exception as e:
        print(f"Error al subir el documento: {e}")
        flash(f"Error al subir el documento: {e}", "error")
        return redirect(url_for('bienvenida'))
    finally:
        if conn:
            conn.close()
    flash("Error desconocido al subir el documento.", "error")
    return redirect(url_for('bienvenida'))


@app.route('/descargar_documento/<int:documento_id>')
def descargar_documento(documento_id):
    """
    Permite descargar un documento por su ID.
    Asegura que el archivo se descargue con su nombre original y el tipo de contenido correcto.
    """
    conn = None
    try:
        conn = get_connection()
        if conn is None:
            abort(500, description="Error: No se pudo conectar a la base de datos para descargar el archivo.")

        cursor = conn.cursor()
        # Seleccionamos también el tipo_contenido
        sql_select = "SELECT nombre_documento, tipo_contenido, datos_documento FROM Documentos WHERE id_documento = ?;"
        cursor.execute(sql_select, documento_id)
        row = cursor.fetchone()

        if row:
            nombre_documento_guardado = row.nombre_documento  # El nombre original al subir
            tipo_contenido = row.tipo_contenido
            datos_documento_binarios = io.BytesIO(row.datos_documento) 

            # **Ajuste clave aquí:**
            # 1. Obtener la extensión del nombre original.
            # 2. Asegurar que el nombre de descarga tenga la extensión correcta.
            #    Esto es crucial para que el navegador lo reconozca como PDF, JPG, etc.
            
            # Extraer la extensión del nombre original del documento
            # Si el nombre_documento_guardado ya incluye la extensión (ej. "mi_tesis.pdf"), la conservamos.
            # Si no, asumimos que el tipo_contenido es "application/pdf" y añadimos ".pdf".
            
            # Por ejemplo, si nombre_documento_guardado es "Mi Informe" y tipo_contenido es "application/pdf"
            # entonces download_name será "Mi Informe.pdf"
            
            _, ext = os.path.splitext(nombre_documento_guardado)
            if not ext and tipo_contenido == 'application/pdf':
                download_name = nombre_documento_guardado + '.pdf'
            elif not ext and tipo_contenido == 'image/jpeg':
                download_name = nombre_documento_guardado + '.jpg'
            elif not ext and tipo_contenido == 'image/png':
                download_name = nombre_documento_guardado + '.png'
            else: # Si ya tiene extensión o es otro tipo, usar el nombre tal cual
                download_name = nombre_documento_guardado

            # Envía el archivo al navegador para su descarga
            return send_file(datos_documento_binarios,
                             mimetype=tipo_contenido, # Usa el tipo_contenido de la base de datos
                             as_attachment=True,
                             download_name=download_name) # Usa el nombre de descarga con la extensión correcta
        else:
            abort(404, description="Documento no encontrado.")
    except Exception as e:
        print(f"Error al descargar el documento: {e}")
        abort(500, description=f"Error al descargar el documento: {e}")
    finally:
        if conn:
            conn.close()

# API para obtener semestres únicos para el select del modal de subida
@app.route('/obtener_semestres_unicos_api', methods=['GET'])
def obtener_semestres_unicos_api():
    conn = None
    semestres = []
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT semestre FROM materias ORDER BY semestre;")
            semestres = [row[0] for row in cursor.fetchall()] # Extrae solo el valor del semestre
    except Exception as e:
        print(f"Error al obtener semestres: {e}")
    finally:
        if conn:
            conn.close()
    return jsonify(semestres)
    #crear comentarios s
@app.route('/api/documentos/<int:id_documento>/comentarios', methods=['POST'])
def crear_comentario(id_documento):
    if 'id' not in session:
        return jsonify({"error": "No autorizado"}), 401

    contenido = request.form.get('contenido', '').strip()
    if not contenido:
        return jsonify({"error": "Comentario vacío"}), 400

    exito = agregar_comentario(id_documento, session['id'], contenido)
    if exito:
        return jsonify({"mensaje": "Comentario agregado correctamente"}), 201
    else:
        return jsonify({"error": "Error al guardar el comentario"}), 500
    #optener los comentarios por docuemtos
@app.route('/api/documentos/<int:id_documento>/comentarios', methods=['GET'])
def obtener_comentarios_documento(id_documento):
    comentarios = obtener_comentarios(id_documento)
    return jsonify(comentarios), 200
    #eliminar los comentarios por docuemtos
@app.route('/api/comentarios/<int:id_comentario>', methods=['DELETE'])
def borrar_comentario(id_comentario):
    if 'id' not in session:
        return jsonify({"error": "No autorizado"}), 401

    exito = eliminar_comentario(id_comentario, session['id'])
    if exito:
        return jsonify({"mensaje": "Comentario eliminado"}), 200
    else:
        return jsonify({"error": "No se pudo eliminar (no eres el autor o error)"}), 403

@app.route('/api/comentarios/<int:id_comentario>', methods=['PUT'])
def actualizar_comentario(id_comentario):
    if 'id' not in session:
        return jsonify({"error": "No autorizado"}), 401

    nuevo_contenido = request.form.get('contenido', '').strip()
    if not nuevo_contenido:
        return jsonify({"error": "Contenido vacío"}), 400

    exito = editar_comentario(id_comentario, session['id'], nuevo_contenido)
    if exito:
        return jsonify({"mensaje": "Comentario actualizado"}), 200
    else:
        return jsonify({"error": "No se pudo editar (no eres el autor o error)"}), 403


# API para obtener materias filtradas por semestre para el select del modal de subida
@app.route('/obtener_materias_por_semestre_api/<semestre>', methods=['GET'])
def obtener_materias_por_semestre_api(semestre):
    conn = None
    materias_filtradas = []
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_materia, nombre_materia FROM materias WHERE semestre = ? ORDER BY nombre_materia;", semestre)
            # Retorna id y nombre de la materia para la selección
            materias_filtradas = [{'id': row[0], 'nombre': row[1]} for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error al obtener materias por semestre: {e}")
    finally:
        if conn:
            conn.close()
    return jsonify(materias_filtradas)
# API para buscar usuarios por nombre para validar nombre desde JS
@app.route('/buscar_nombre/<nombre>', methods=['GET'])
def buscar_por_nombre_api(nombre):
    usuario = buscar_usuario_por_nombre(nombre)
    if usuario:
        return jsonify(usuario)
    else:
        abort(404, description="Usuario no encontrado")

# Funcion para verificar usuario (login) desde JS si es administrador o no
def verificar_usuario(correo, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, nombre, correo, password, rol FROM usuarios WHERE correo = ?", (correo,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row and bcrypt.checkpw(password.encode('utf-8'), row[3].encode('utf-8')):
            return {"id": row[0], "nombre": row[1], "correo": row[2], "rol": row[4]}
        else:
            return None
    except Exception as e:
        print("Error al verificar usuario:", e)
        return None

@app.route('/api/documentos/<int:id_documento>', methods=['DELETE'])
def api_eliminar_documento(id_documento):
    if 'id' not in session:
        return jsonify({"error": "No autorizado"}), 401

    id_usuario_actual = session['id']
    resultado, status_code = eliminar_documento(id_documento, id_usuario_actual)
    return jsonify(resultado), status_code



# Ruta para crear una nueva materia (solo accesible por administradores)
@app.route('/admin/crear_materia', methods=['GET', 'POST'])
def crear_materia():
    if 'rol' not in session or session['rol'] != 'admin':
        flash("Acceso denegado.", "error")
        return redirect(url_for('admin'))
    if request.method == 'POST':
        nombre = request.form['nombre']
        semestre = request.form['semestre']
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO materias (nombre_materia, semestre) VALUES (?, ?)", (nombre, semestre))
        conn.commit()
        conn.close()
        flash("Materia creada correctamente.", "success")
        return redirect(url_for('admin'))
    return render_template('crear_materia.html')

if __name__ == '__main__':
    # Ejecuta la aplicación en modo depuración (debug=True)
    # Cambia debug=False para producción
    app.run(debug=True, host='0.0.0.0', port=5000)