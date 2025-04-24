from conexion_database import get_connection
import bcrypt

def insertar_usuario(nombre, correo, password):
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
