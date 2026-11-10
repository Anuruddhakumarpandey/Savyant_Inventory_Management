
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth.login"

    from app.routes.auth import auth
    app.register_blueprint(auth)

    from app.routes.main import main
    app.register_blueprint(main)

    from app.routes.customers import customers
    app.register_blueprint(customers)

    from app.routes.products import products
    app.register_blueprint(products)

    from app.routes.inventory import inventory
    app.register_blueprint(inventory)

    from app.routes.sales_orders import sales_orders
    app.register_blueprint(sales_orders)

    from app.routes.api import api
    app.register_blueprint(api)

    from app.routes.reports import reports
    app.register_blueprint(reports)

    from app.routes.csv_import import csv_import
    app.register_blueprint(csv_import)

    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return db.session.get(User, int(user_id))
