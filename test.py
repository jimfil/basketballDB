import bcrypt
# Hash the password "admin123"
password_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode('utf-8')
print(password_hash)