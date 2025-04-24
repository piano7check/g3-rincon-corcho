from conexion_database import get_connection
import bcrypt
from validaciones import es_email_valido, es_password_seguro
def insertar_usuario(nombre, correo, password):
    if not nombre or not correo or not password:
        return False
    if not es_email_valido(correo):
        print("Correo inválido")
        return False
    if not es_password_seguro(password):
        print("Contraseña no segura")
        return False
    try:
        
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, correo, password) VALUES (?, ?, ?)", (nombre, correo, hashed))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print("Error al insertar:", e)
        return False
