def editar_usuario(id_usuario, nuevo_nombre, nuevo_correo, nuevo_foto=None, nueva_password=None):
    from conexion_database import get_connection
    from buscar_usuarios import buscar_usuario_por_correo
    from validaciones import es_email_valido
    import bcrypt

    if not nuevo_nombre or not nuevo_correo:
        print("Nombre y correo son requeridos.")
        return False

    if not es_email_valido(nuevo_correo):
        return False

    usuario_existente = buscar_usuario_por_correo(nuevo_correo)
    if usuario_existente and usuario_existente['id'] != id_usuario:
        return False

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = "UPDATE usuarios SET nombre = ?, correo = ?"
        valores = [nuevo_nombre, nuevo_correo]

        if nuevo_foto:
            query += ", foto = ?"
            valores.append(nuevo_foto)

        if nueva_password:
            hashed = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt())
            query += ", password = ?"
            valores.append(hashed)

        query += " WHERE id_usuario = ?"
        valores.append(id_usuario)

        cursor.execute(query, tuple(valores))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ Error al editar usuario:", e)
        return False
