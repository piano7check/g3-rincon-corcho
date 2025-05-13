import re

def es_nombre_valido(nombre):
    return bool(nombre.strip())

def es_email_valido(correo):
    return correo.endswith("@uab.edu.bo")

def es_password_seguro(password):
    if len(password) < 8:
        return False
    if not re.search(r'[0-9\W]', password):  # Debe tener al menos un número o símbolo
        return False
    return True
