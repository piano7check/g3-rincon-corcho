from conexion_database import get_connection

def eliminar_documento(id_documento, id_usuario_actual):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Verificar si el documento existe y pertenece al usuario autenticado
        cursor.execute("SELECT id_usuario FROM documentos WHERE id_documento = ?", (id_documento,))
        row = cursor.fetchone()

        if not row:
            return {"error": "Documento no encontrado"}, 404

        id_usuario_documento = row[0]
        if id_usuario_documento != id_usuario_actual:
            return {"error": "No tienes permiso para eliminar este documento"}, 403

        # Eliminar el documento de la base de datos
        cursor.execute("DELETE FROM documentos WHERE id_documento = ?", (id_documento,))
        conn.commit()
        cursor.close()
        conn.close()

        return {"mensaje": "Documento eliminado correctamente"}, 200

    except Exception as e:
        print("Error eliminando documento:", e)
        return {"error": "Error del servidor al eliminar el documento"}, 500