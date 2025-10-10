from app.core.security import hash_password, verify_password

plain_password = "Hello123"
hashed_password = hash_password(plain_password)
print(hashed_password)

print(verify_password(plain_password, hashed_password))
