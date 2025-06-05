from conexion_database import get_connection

def obtener_carpetas_usuario(id_usuario):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT m.id_materia, m.nombre_materia
            FROM Documentos d
            JOIN Materias m ON d.id_materia = m.id_materia
            WHERE d.id_usuario = ?
        """, (id_usuario,))
        filas = cursor.fetchall()
        cursor.close()
        conn.close()
        return [{"id": row[0], "nombre": row[1]} for row in filas]
    except Exception as e:
        print("❌ Error al obtener carpetas del usuario:", e)
        return []
