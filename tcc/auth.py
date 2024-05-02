from werkzeug.security import generate_password_hash, check_password_hash

# Hashear una contraseña
hashed_password = generate_password_hash('#Tech1Cash2Club3')
print(hashed_password)

# Verificar la contraseña
check_password_hash(hashed_password, '')  # Devuelve True si coincide
