from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from decimal import Decimal, InvalidOperation

from app import db
from app.models import Product, StockMovement
from app.routes.decorators import role_required

products = Blueprint("products", __name__)


@products.route("/products")
@login_required
@role_required("Admin")
def product_list():

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    category = request.args.get("category", "").strip()

    query = Product.query

    categories = [
        row[0] for row in db.session.query(Product.category)
        .filter(
            Product.category.isnot(None),
            Product.category != ""
        )
        .distinct()
        .order_by(Product.category)
        .all()
    ]

    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f"%{search}%"),
                Product.product_code.ilike(f"%{search}%"),
                Product.category.ilike(f"%{search}%")
            )
        )

    if status == "active":
        query = query.filter_by(is_active=True)

    elif status == "inactive":
        query = query.filter_by(is_active=False)

    if category:
        query = query.filter(Product.category == category)

    all_products = query.order_by(
        Product.id.desc()
    ).all()

    return render_template(
        "products.html",
        products=all_products,
        search=search,
        status=status,
        category=category,
        categories=categories
    )


@products.route("/products/add", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def add_product():

    if request.method == "POST":

        product_code = request.form.get("product_code", "").strip()
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()

        if not product_code or not name:
            flash("Product code and name are required.", "danger")
            return redirect(url_for("products.add_product"))

        existing_product = Product.query.filter_by(
            product_code=product_code
        ).first()

        if existing_product:
            flash("Product code already exists.", "danger")
            return redirect(url_for("products.add_product"))

        try:
            price = Decimal(request.form.get("price", ""))
            stock_quantity = int(request.form.get("stock_quantity", ""))

            if not price.is_finite() or price < 0 or stock_quantity < 0:
                raise ValueError

        except (InvalidOperation, ValueError):
            flash("Enter valid price and stock quantity.", "danger")
            return redirect(url_for("products.add_product"))

        product = Product(
            product_code=product_code,
            name=name,
            category=category or None,
            price=price,
            stock_quantity=stock_quantity
        )

        db.session.add(product)
        db.session.flush()

        if stock_quantity > 0:
            movement = StockMovement(
                product_id=product.id,
                movement_type="IN",
                quantity_change=stock_quantity,
                reason="Opening stock",
                created_by=current_user.id
            )

            db.session.add(movement)

        db.session.commit()

        flash("Product added successfully!", "success")

        return redirect(url_for("products.product_list"))

    return render_template("product_form.html")


@products.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def edit_product(product_id):

    product = db.session.get(Product, product_id)

    if product is None:
        return "Product not found", 404

    if request.method == "POST":

        product_code = request.form.get("product_code", "").strip()
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()

        if not product_code or not name:
            flash("Product code and name are required.", "danger")
            return redirect(url_for(
                "products.edit_product",
                product_id=product.id
            ))

        existing_product = Product.query.filter(
            Product.product_code == product_code,
            Product.id != product.id
        ).first()

        if existing_product:
            flash("Product code already exists.", "danger")
            return redirect(url_for(
                "products.edit_product",
                product_id=product.id
            ))

        try:
            price = Decimal(request.form.get("price", ""))

            if not price.is_finite() or price < 0:
                raise ValueError

        except (InvalidOperation, ValueError):
            flash("Enter a valid price.", "danger")
            return redirect(url_for(
                "products.edit_product",
                product_id=product.id
            ))

        product.product_code = product_code
        product.name = name
        product.category = category or None
        product.price = price

        db.session.commit()

        flash("Product updated successfully!", "success")

        return redirect(url_for("products.product_list"))

    return render_template(
        "product_form.html",
        product=product
    )




@products.route("/products/deactivate/<int:product_id>", methods=["POST"])
@login_required
@role_required("Admin")
def deactivate_product(product_id):

    product = db.session.get(Product, product_id)

    if product is None:
        return "Product not found", 404

    product.is_active = False

    db.session.commit()

    flash("Product deactivated successfully!", "success")

    return redirect(url_for("products.product_list"))



@products.route("/products/reactivate/<int:product_id>", methods=["POST"])
@login_required
@role_required("Admin")
def reactivate_product(product_id):

    product = db.session.get(Product, product_id)

    if product is None:
        return "Product not found", 404

    product.is_active = True

    db.session.commit()

    flash("Product reactivated successfully!", "success")

    return redirect(url_for("products.product_list"))