from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import Product, StockMovement
from app.routes.decorators import role_required

inventory = Blueprint("inventory", __name__)


@inventory.route("/inventory", methods=["GET"])
@login_required
@role_required("Admin")
def inventory_list():

    all_products = Product.query.order_by(Product.id.desc()).all()

    return render_template(
        "inventory.html",
        products=all_products
    )


@inventory.route("/inventory/adjust/<int:product_id>", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def adjust_stock(product_id):

    product = db.session.get(Product, product_id)

    if product is None:
        return "Product not found", 404

    if request.method == "POST":

        movement_type = request.form.get("movement_type", "").strip()
        reason = request.form.get("reason", "").strip()

        try:
            quantity = int(request.form.get("quantity", ""))

            if quantity <= 0:
                raise ValueError

        except ValueError:
            flash("Enter a valid positive quantity.", "danger")
            return redirect(url_for(
                "inventory.adjust_stock",
                product_id=product.id
            ))

        if movement_type not in ["IN", "OUT"]:
            flash("Invalid stock movement type.", "danger")
            return redirect(url_for(
                "inventory.adjust_stock",
                product_id=product.id
            ))

        if not reason:
            flash("Reason is required.", "danger")
            return redirect(url_for(
                "inventory.adjust_stock",
                product_id=product.id
            ))

        try:
            product = Product.query.filter_by(
                id=product_id
            ).with_for_update().first()

            if movement_type == "OUT" and product.stock_quantity < quantity:
                db.session.rollback()
                flash("Insufficient stock available.", "danger")
                return redirect(url_for(
                    "inventory.adjust_stock",
                    product_id=product.id
                ))

            if movement_type == "IN":
                product.stock_quantity += quantity
                quantity_change = quantity

            else:
                product.stock_quantity -= quantity
                quantity_change = -quantity

            movement = StockMovement(
                product_id=product.id,
                movement_type=movement_type,
                quantity_change=quantity_change,
                reason=reason,
                created_by=current_user.id
            )

            db.session.add(movement)
            db.session.commit()

            flash("Stock adjusted successfully!", "success")

        except Exception:
            db.session.rollback()
            raise

        return redirect(url_for("inventory.inventory_list"))

    return render_template(
        "inventory_form.html",
        product=product
    )


@inventory.route("/inventory/history")
@login_required
@role_required("Admin")
def stock_history():

    movements = (
        StockMovement.query
        .join(Product, StockMovement.product_id == Product.id)
        .add_columns(Product.name, Product.product_code)
        .order_by(StockMovement.created_at.desc())
        .all()
    )

    return render_template(
        "stock_history.html",
        movements=movements
    )