import bcrypt

# Tu contraseña en texto plano
password = "Admin@123456"

# Generar el hash
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

print(hashed.decode())