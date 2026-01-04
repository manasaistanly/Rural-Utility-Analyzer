from app.core.database import SessionLocal
from app.models.models import User
from app.core.security import get_password_hash

db = SessionLocal()

def create_demo_user():
    username = "demo"
    password = "demo123"
    
    # Check if exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        print(f"User '{username}' already exists.")
        return

    hashed_password = get_password_hash(password)
    demo_user = User(
        username=username,
        email="demo@example.com",
        hashed_password=hashed_password,
        language_pref="en"
    )
    
    db.add(demo_user)
    db.commit()
    print(f"Successfully created user '{username}' with password '{password}'")

if __name__ == "__main__":
    create_demo_user()
