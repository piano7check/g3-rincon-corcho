from conexion_database import get_connection

def buscar_usuario_por_id(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, nombre, correo, foto FROM usuarios WHERE id_usuario = ?", (id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return {
                "id": row[0],
                "nombre": row[1],
                "correo": row[2],
                "foto": row[3]
            }
        return None
    except Exception as e:
        print("Error al buscar por ID:", e)
        return None

def buscar_usuario_por_correo(correo):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, nombre, correo FROM usuarios WHERE correo = ?", (correo,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return {"id": row[0], "nombre": row[1], "correo": row[2]}
        return None
    except Exception as e:
        print("Error al buscar por correo:", e)
        return None
    
#Funcion para buscar un usuario por nombre, y que no se repita el nombre en la base de datos
def buscar_usuario_por_nombre(nombre):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, nombre, correo FROM usuarios WHERE nombre = ?", (nombre,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return {"id": row[0], "nombre": row[1], "correo": row[2]}
        return None
    except Exception as e:
        print("Error al buscar por nombre:", e)
        return None

def correo_existe(correo):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM usuarios WHERE correo = ?", (correo,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row is not None  # Devuelve True si el correo existe, False si no
    except Exception as e:
        print("Error al verificar correo:", e)
        return False

