"""
Run once to create your first admin login:
    python create_admin.py
"""
from app.database import SessionLocal, Base, engine
from app import models, auth

Base.metadata.create_all(bind=engine)

db = SessionLocal()

username = input("Admin username: ")
password = input("Admin password: ")

existing = db.query(models.User).filter(models.User.username == username).first()
if existing:
    print("User already exists.")
else:
    user = models.User(username=username, password_hash=auth.hash_password(password), role="admin")
    db.add(user)
    db.commit()
    print(f"Admin user '{username}' created.")

db.close()
