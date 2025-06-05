from conexion_database import get_connection
import bcrypt

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
