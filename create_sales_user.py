from app import create_app, db, bcrypt
from app.models import User
from getpass import getpass

app = create_app()

with app.app_context():
    name = input("Enter sales user name: ")
    email = input("Enter sales user email: ")
    password = getpass("Enter sales user password: ")

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        print("User already exists!")
    else:
        sales_user = User(
            name=name,
            email=email,
            password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
            role="Sales User"
        )

        db.session.add(sales_user)
        db.session.commit()

        print("Sales User created successfully!")