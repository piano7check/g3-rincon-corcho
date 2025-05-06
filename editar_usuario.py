from conexion_database import get_connection
from buscar_usuarios import buscar_usuario_por_correo
from validaciones import es_nombre_valido, es_email_valido

def editar_usuario(id_usuario, nuevo_nombre, nuevo_correo):
    
    if not nuevo_nombre or not nuevo_correo:
        print("Error: El nombre y el correo no pueden estar vacíos.")
        return False
    
    if not es_email_valido(nuevo_correo):
        print("Error: El correo electrónico no es válido.")
        return False
    
    usuario_existente = buscar_usuario_por_correo(nuevo_correo)
    
    if(usuario_existente and usuario_existente['id'] != id_usuario):
        print("El correo ya esta registrado por otro usuario.")
        return False
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET nombre = ?, correo = ? WHERE id_usuario = ?",
            (nuevo_nombre, nuevo_correo, id_usuario)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    
    except Exception as e:
        print("Error al editar:", e)
        return False
    