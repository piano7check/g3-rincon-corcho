from conexion_database import get_connection



def obtener_todos_los_usuarios():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        usuarios = []
        for row in rows:
            usuarios.append({
                "id": row[0],
                "nombre": row[1],
                "correo": row[2]
            })
        return usuarios
    except Exception as e:
        print("Error al obtener usuarios:", e)
        return []
