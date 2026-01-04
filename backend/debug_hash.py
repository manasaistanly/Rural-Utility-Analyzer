from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

try:
    print("Hashing password...")
    hash = pwd_context.hash("demo123")
    print(f"Hash: {hash}")
except Exception as e:
    print(f"Error: {e}")
