from conexion_database import get_connection

def obtener_todos_los_usuarios():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT u.id_usuario, u.nombre, u.correo, u.rol, u.solicitud_admin,
                   COUNT(d.id_documento) AS cantidad_documentos
            FROM usuarios u
            LEFT JOIN documentos d ON u.id_usuario = d.id_usuario
            GROUP BY u.id_usuario, u.nombre, u.correo, u.rol, u.solicitud_admin
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        usuarios = []
        for row in rows:
            usuarios.append({
                "id": row[0],
                "nombre": row[1],
                "correo": row[2],
                "rol": row[3],
                "solicitud_admin": row[4],
                "cantidad_documentos": row[5]
            })

        return usuarios

    except Exception as e:
        print("Error al obtener usuarios:", e)
        return []

