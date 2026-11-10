from app import create_app, db, bcrypt
from app.models import User
from getpass import getpass

app = create_app()

with app.app_context():
    name = input("Enter admin name: ")
    email = input("Enter admin email: ")
    password = getpass("Enter admin password: ")

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        print("User already exists!")
    else:
        admin = User(
            name=name,
            email=email,
            password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
            role="Admin"
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin created successfully!")