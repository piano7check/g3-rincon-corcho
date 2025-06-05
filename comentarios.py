from conexion_database import get_connection
from flask import session
from datetime import datetime


def agregar_comentario(documento_id, usuario_id, contenido):
    import traceback
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Asumiendo que la columna 'fecha' tiene valor por defecto en la BD
        cursor.execute("""
            INSERT INTO comentarios (id_documento, id_usuario, contenido)
            VALUES (?, ?, ?)
        """, (documento_id, usuario_id, contenido))

        conn.commit()
        return True
    except Exception as e:
        print("Error al agregar comentario:", e)
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()


def obtener_comentarios(documento_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id_comentario, c.contenido, c.fecha, u.nombre, c.id_usuario
            FROM comentarios c
            INNER JOIN usuarios u ON c.id_usuario = u.id_usuario
            WHERE c.id_documento = ?
            ORDER BY c.fecha DESC
        """, (documento_id,))
        comentarios = cursor.fetchall()

        user_id = session.get('id')  # obtener id del usuario logueado
        return [
            {
                "id_comentario": row[0],
                "contenido": row[1],
                "fecha": row[2].strftime("%d/%m/%Y %H:%M"),  # formato legible
                "autor": row[3],
                "es_autor": (row[4] == user_id)  # True si el comentario es del usuario actual
            }
            for row in comentarios
        ]
    except Exception as e:
        print("Error al obtener comentarios:", e)
        return []
    finally:
        if conn:
            conn.close()



def eliminar_comentario(id_comentario, id_usuario):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM comentarios 
            WHERE id_comentario = ? AND id_usuario = ?
        """, (id_comentario, id_usuario))

        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print("Error al eliminar comentario:", e)
        return False
    finally:
        if conn:
            conn.close()

def editar_comentario(id_comentario, id_usuario, nuevo_contenido):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE comentarios
            SET contenido = ?
            WHERE id_comentario = ? AND id_usuario = ?
        """, (nuevo_contenido, id_comentario, id_usuario))

        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print("Error al editar comentario:", e)
        return False
    finally:
        if conn:
            conn.close()

