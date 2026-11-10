from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    __table_args__ = (
        db.CheckConstraint(
            "role IN ('Admin', 'Sales User')",
            name="check_user_role"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False , index=True)
    email = db.Column(db.String(120))
    mobile = db.Column(db.String(15))
    city = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True, nullable=False)


class Product(db.Model):
    __tablename__ = "products"
    __table_args__ = (
    db.CheckConstraint(
        "price >= 0",
        name="check_product_price"
    ),
    db.CheckConstraint(
        "stock_quantity >= 0",
        name="check_stock_quantity"
    ),
)

    id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False, index=True)
    category = db.Column(db.String(100))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)


class SalesOrder(db.Model):
    __tablename__ = "sales_orders"
    __table_args__ = (
    db.CheckConstraint(
        "status IN ('Draft', 'Confirmed', 'Cancelled')",
        name="check_order_status"
    ),
    db.CheckConstraint(
        "discount_percent >= 0 AND discount_percent <= 20",
        name="check_discount_percent"
    ),
)

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)

    customer_id = db.Column(
        db.Integer, db.ForeignKey("customers.id"), nullable=False
    )

    order_date = db.Column(
        db.DateTime, server_default=db.func.current_timestamp()
    )

    status = db.Column(db.String(20), default="Draft", nullable=False)
    discount_percent = db.Column(db.Numeric(5, 2), default=0, nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), default=0, nullable=False)
    discount_amount = db.Column(db.Numeric(12, 2), default=0, nullable=False)
    grand_total = db.Column(db.Numeric(12, 2), default=0, nullable=False)

    created_by = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )


class SalesOrderItem(db.Model):
    __tablename__ = "sales_order_items"
    __table_args__ = (
    db.UniqueConstraint(
        "sales_order_id",
        "product_id",
        name="unique_product_per_order"
    ),
    db.CheckConstraint(
        "quantity > 0",
        name="check_quantity_positive"
    ),
    db.CheckConstraint(
        "rate >= 0 AND amount >= 0",
        name="check_order_item_amount"
    ),
)

    id = db.Column(db.Integer, primary_key=True)

    sales_order_id = db.Column(
        db.Integer, db.ForeignKey("sales_orders.id"), nullable=False, index=True
    )

    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id"), nullable=False, index=True
    )

    quantity = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Numeric(10, 2), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)


class StockMovement(db.Model):
    __tablename__ = "stock_movements"

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id"), nullable=False, index=True
    )

    movement_type = db.Column(db.String(20), nullable=False)
    quantity_change = db.Column(db.Integer, nullable=False)

    order_id = db.Column(
        db.Integer, db.ForeignKey("sales_orders.id"), nullable=True,index=True
    )

    reason = db.Column(db.String(255))

    created_by = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )

    created_at = db.Column(
        db.DateTime, server_default=db.func.current_timestamp()
    )