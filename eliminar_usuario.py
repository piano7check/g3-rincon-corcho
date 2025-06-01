from conexion_database import get_connection

def eliminar_usuario_por_id(id_usuario):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id_usuario = ?", (id_usuario,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print("Error al eliminar usuario:", e)
        return False