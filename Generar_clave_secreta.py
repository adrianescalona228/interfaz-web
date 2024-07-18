import secrets

# Generar una clave secreta
secret_key = secrets.token_hex(48)  # Genera una cadena hexadecimal de 16 bytes

print("Clave secreta generada:", secret_key)
