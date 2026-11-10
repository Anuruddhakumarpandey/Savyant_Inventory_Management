from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from decimal import Decimal, InvalidOperation
from app import db
from app.models import SalesOrder, SalesOrderItem, Customer, Product, StockMovement
from app.routes.decorators import role_required
from uuid import uuid4

sales_orders = Blueprint("sales_orders", __name__)
@sales_orders.route("/sales-orders")
@login_required
def sales_order_list():

    

 if current_user.role == "Admin":
    orders = SalesOrder.query.order_by(
        SalesOrder.id.desc()
    ).all()
 else:
    orders = SalesOrder.query.filter_by(
        created_by=current_user.id
    ).order_by(
        SalesOrder.id.desc()
    ).all()   




    return render_template(
        "sales_orders.html",
        orders=orders
    )

@sales_orders.route("/sales-orders/<int:order_id>")
@login_required
def sales_order_detail(order_id):

    order = db.session.get(SalesOrder, order_id)

    if order is None:
        return "Sales Order not found", 404

    if current_user.role != "Admin" and order.created_by != current_user.id:
     return "Access denied", 403


    

    items = (
        db.session.query(SalesOrderItem, Product)
        .join(Product, SalesOrderItem.product_id == Product.id)
        .filter(SalesOrderItem.sales_order_id == order.id)
        .all()
    )

    return render_template(
        "sales_order_detail.html",
        order=order,
        items=items
    )

@sales_orders.route(
    "/sales-orders/<int:order_id>/status",
    methods=["POST"]
)
@login_required
def update_order_status(order_id):

    action = request.form.get("action")

    try:
        order = (
            SalesOrder.query
            .filter_by(id=order_id)
            .with_for_update()
            .first()
        )

        if order is None:
            return "Sales Order not found", 404

        if current_user.role != "Admin" and order.created_by != current_user.id:
         return "Access denied", 403

        if action == "confirm":

            if order.status != "Draft":
                flash("Only Draft orders can be confirmed.", "danger")
                return redirect(
                    url_for("sales_orders.sales_order_detail",
                            order_id=order.id)
                )

            items = SalesOrderItem.query.filter_by(
                sales_order_id=order.id
            ).all()

            product_ids = sorted(item.product_id for item in items)

            locked_products = (
                Product.query
                .filter(Product.id.in_(product_ids))
                .order_by(Product.id)
                .with_for_update()
                .all()
            )

            product_map = {
                product.id: product for product in locked_products
            }

            for item in items:
                product = product_map.get(item.product_id)

                if product is None or product.stock_quantity < item.quantity:
                    db.session.rollback()
                    flash("Insufficient stock available.", "danger")
                    return redirect(
                        url_for("sales_orders.sales_order_detail",
                                order_id=order.id)
                    )

            for item in items:
                product = product_map[item.product_id]

                product.stock_quantity -= item.quantity

                movement = StockMovement(
                    product_id=product.id,
                    movement_type="OUT",
                    quantity_change=-item.quantity,
                    order_id=order.id,
                    reason=f"Sales Order {order.order_number} confirmed",
                    created_by=current_user.id
                )

                db.session.add(movement)

            order.status = "Confirmed"

        elif action == "cancel":

            if order.status not in ["Draft", "Confirmed"]:
                flash("This order cannot be cancelled.", "danger")
                return redirect(
                    url_for("sales_orders.sales_order_detail",
                            order_id=order.id)
                )

            if order.status == "Confirmed":

                items = SalesOrderItem.query.filter_by(
                    sales_order_id=order.id
                ).all()

                product_ids = sorted(item.product_id for item in items)

                locked_products = (
                    Product.query
                    .filter(Product.id.in_(product_ids))
                    .order_by(Product.id)
                    .with_for_update()
                    .all()
                )

                product_map = {
                    product.id: product for product in locked_products
                }

                for item in items:
                    product = product_map[item.product_id]

                    product.stock_quantity += item.quantity

                    movement = StockMovement(
                        product_id=product.id,
                        movement_type="IN",
                        quantity_change=item.quantity,
                        order_id=order.id,
                        reason=f"Sales Order {order.order_number} cancelled",
                        created_by=current_user.id
                    )

                    db.session.add(movement)

            order.status = "Cancelled"

        else:
            flash("Invalid order action.", "danger")
            return redirect(
                url_for("sales_orders.sales_order_detail",
                        order_id=order.id)
            )

        db.session.commit()
        flash("Order status updated successfully!", "success")

    except Exception:
        db.session.rollback()
        raise

    return redirect(
        url_for("sales_orders.sales_order_detail",
                order_id=order_id)
    )


@sales_orders.route("/sales-orders/create", methods=["GET", "POST"])
@login_required
def create_sales_order():

    customers = Customer.query.filter_by(
        is_active=True
    ).all()

    products = Product.query.filter_by(
        is_active=True
    ).all()

    if request.method == "POST":

        try:
            customer_id = int(request.form.get("customer_id"))

            customer = db.session.get(Customer, customer_id)

            if customer is None or not customer.is_active:
                flash("Please select a valid customer.", "danger")
                return redirect(url_for("sales_orders.create_sales_order"))

            discount_percent = Decimal(
                request.form.get("discount_percent", "0")
            )

            if discount_percent < 0 or discount_percent > 20:
                flash("Discount must be between 0 and 20%.", "danger")
                return redirect(url_for("sales_orders.create_sales_order"))

            order_items = []
            subtotal = Decimal("0.00")

            for product in products:

                quantity_value = request.form.get(
                    f"quantity_{product.id}", "0"
                )

                quantity = int(quantity_value or 0)

                if quantity < 0:
                    raise ValueError

                if quantity > 0:

                    rate = Decimal(str(product.price))
                    amount = rate * quantity

                    order_items.append({
                        "product": product,
                        "quantity": quantity,
                        "rate": rate,
                        "amount": amount
                    })

                    subtotal += amount

            if not order_items:
                flash("Please select at least one product.", "danger")
                return redirect(url_for("sales_orders.create_sales_order"))

            discount_amount = (
                subtotal * discount_percent / Decimal("100")
            ).quantize(Decimal("0.01"))

            grand_total = subtotal - discount_amount

            order = SalesOrder(
                order_number="ORD-" + uuid4().hex[:12].upper(),
                customer_id=customer.id,
                discount_percent=discount_percent,
                subtotal=subtotal,
                discount_amount=discount_amount,
                grand_total=grand_total,
                status="Draft",
                created_by=current_user.id
            )

            db.session.add(order)
            db.session.flush()

            for item in order_items:

                order_item = SalesOrderItem(
                    sales_order_id=order.id,
                    product_id=item["product"].id,
                    quantity=item["quantity"],
                    rate=item["rate"],
                    amount=item["amount"]
                )

                db.session.add(order_item)

            db.session.commit()

            flash("Sales Order created successfully!", "success")

            return redirect(url_for("sales_orders.sales_order_list"))

        except (ValueError, InvalidOperation):
            db.session.rollback()
            flash("Please enter valid order details.", "danger")

        except Exception:
            db.session.rollback()
            raise

    return render_template(
        "sales_order_form.html",
        customers=customers,
        products=products
    )