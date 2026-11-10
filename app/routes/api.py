from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from app import db
from app.models import Product, Customer, SalesOrder, SalesOrderItem , StockMovement

api = Blueprint("api", __name__, url_prefix="/api")


# GET API: Active Products
@api.route("/products", methods=["GET"])
@login_required
def get_products():

    products = Product.query.filter_by(
        is_active=True
    ).all()

    product_list = []

    for product in products:
        product_list.append({
            "id": product.id,
            "product_code": product.product_code,
            "name": product.name,
            "category": product.category,
            "price": float(product.price),
            "stock_quantity": product.stock_quantity
        })

    return jsonify({
        "success": True,
        "products": product_list
    }), 200


# POST API: Create Sales Order
@api.route("/orders", methods=["POST"])
@login_required
def create_order_api():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid JSON data"
        }), 400

    customer_id = data.get("customer_id")
    items = data.get("items", [])
    discount = data.get("discount_percent", 0)

    if not customer_id:
        return jsonify({
            "success": False,
            "message": "Customer ID is required"
        }), 400

    if not isinstance(items, list) or not items:
        return jsonify({
            "success": False,
            "message": "At least one product is required"
        }), 400

    customer = Customer.query.filter_by(
        id=customer_id,
        is_active=True
    ).first()

    if not customer:
        return jsonify({
            "success": False,
            "message": "Invalid or inactive customer"
        }), 400

    try:
        discount = Decimal(str(discount))
    except (InvalidOperation, TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Invalid discount"
        }), 400

    if not discount.is_finite() or discount < 0 or discount > 20:
        return jsonify({
            "success": False,
            "message": "Discount must be between 0 and 20"
        }), 400

    subtotal = Decimal("0.00")
    order_items = []
    used_products = set()

    for item in items:

        if not isinstance(item, dict):
            return jsonify({
                "success": False,
                "message": "Invalid product item"
            }), 400

        product_id = item.get("product_id")
        quantity = item.get("quantity")

        if (
            not isinstance(product_id, int)
            or isinstance(product_id, bool)
            or not isinstance(quantity, int)
            or isinstance(quantity, bool)
            or quantity <= 0
        ):
            return jsonify({
                "success": False,
                "message": "Invalid product ID or quantity"
            }), 400

        if product_id in used_products:
            return jsonify({
                "success": False,
                "message": "Duplicate products are not allowed"
            }), 400

        used_products.add(product_id)

        product = Product.query.filter_by(
            id=product_id,
            is_active=True
        ).first()

        if not product:
            return jsonify({
                "success": False,
                "message": "Invalid or inactive product"
            }), 400

        rate = Decimal(str(product.price))
        amount = rate * quantity
        subtotal += amount

        order_items.append({
            "product": product,
            "quantity": quantity,
            "rate": rate,
            "amount": amount
        })

    subtotal = subtotal.quantize(Decimal("0.01"))

    discount_amount = (
        subtotal * discount / Decimal("100")
    ).quantize(Decimal("0.01"))

    grand_total = subtotal - discount_amount

    try:
        order = SalesOrder(
            order_number="ORD-" + uuid4().hex[:12].upper(),
            customer_id=customer.id,
            status="Draft",
            discount_percent=discount,
            subtotal=subtotal,
            discount_amount=discount_amount,
            grand_total=grand_total,
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

        return jsonify({
            "success": True,
            "message": "Sales order created successfully",
            "order_id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "subtotal": float(subtotal),
            "discount_amount": float(discount_amount),
            "grand_total": float(grand_total)
        }), 201

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Unable to create sales order"
        }), 500




@api.route("/orders/<int:order_id>", methods=["GET"])
@login_required
def get_order_api(order_id):

    order = SalesOrder.query.get(order_id)

    if not order:
        return jsonify({
            "success": False,
            "message": "Order not found"
        }), 404

    # Sales User can access only their own orders
    if current_user.role != "Admin" and order.created_by != current_user.id:
        return jsonify({
            "success": False,
            "message": "Access denied"
        }), 403

    items = db.session.query(
        SalesOrderItem, Product
    ).join(
        Product,
        SalesOrderItem.product_id == Product.id
    ).filter(
        SalesOrderItem.sales_order_id == order.id
    ).all()

    item_list = []

    for order_item, product in items:
        item_list.append({
            "product_id": product.id,
            "product_name": product.name,
            "product_code": product.product_code,
            "quantity": order_item.quantity,
            "rate": float(order_item.rate),
            "amount": float(order_item.amount)
        })

    return jsonify({
        "success": True,
        "order": {
            "id": order.id,
            "order_number": order.order_number,
            "customer_id": order.customer_id,
            "status": order.status,
            "subtotal": float(order.subtotal),
            "discount_percent": float(order.discount_percent),
            "discount_amount": float(order.discount_amount),
            "grand_total": float(order.grand_total),
            "items": item_list
        }
    }), 200




@api.route("/orders/<int:order_id>/confirm", methods=["POST"])
@login_required
def confirm_order_api(order_id):

    try:
        order = SalesOrder.query.filter_by(
            id=order_id
        ).with_for_update().first()

        if not order:
            return jsonify({
                "success": False,
                "message": "Order not found"
            }), 404

        if current_user.role != "Admin" and order.created_by != current_user.id:
            return jsonify({
                "success": False,
                "message": "Access denied"
            }), 403

        if order.status != "Draft":
            return jsonify({
                "success": False,
                "message": "Only Draft orders can be confirmed"
            }), 400

        items = SalesOrderItem.query.filter_by(
            sales_order_id=order.id
        ).order_by(
            SalesOrderItem.product_id
        ).all()

        if not items:
            return jsonify({
                "success": False,
                "message": "Order has no products"
            }), 400

        products = {}

        for item in items:
            product = Product.query.filter_by(
                id=item.product_id
            ).with_for_update().first()

            if not product:
                db.session.rollback()
                return jsonify({
                    "success": False,
                    "message": "Product not found"
                }), 404

            if product.stock_quantity < item.quantity:
                db.session.rollback()
                return jsonify({
                    "success": False,
                    "message": "Insufficient stock for " + product.name
                }), 400

            products[item.product_id] = product

        for item in items:
            product = products[item.product_id]

            product.stock_quantity -= item.quantity

            movement = StockMovement(
                product_id=product.id,
                movement_type="OUT",
                quantity_change=-item.quantity,
                order_id=order.id,
                reason="Sales order confirmed",
                created_by=current_user.id
            )

            db.session.add(movement)

        order.status = "Confirmed"

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Order confirmed successfully",
            "order_id": order.id,
            "status": order.status
        }), 200

    except Exception:
        import traceback

        db.session.rollback()

        traceback.print_exc()

        return jsonify({
            "success": False,
            "message": "Unable to confirm order"
        }), 500

# POST API: Cancel Sales Order
@api.route("/orders/<int:order_id>/cancel", methods=["POST"])
@login_required
def cancel_order_api(order_id):

    try:
        order = SalesOrder.query.filter_by(
            id=order_id
        ).with_for_update().first()

        if not order:
            return jsonify({
                "success": False,
                "message": "Order not found"
            }), 404

        if current_user.role != "Admin" and order.created_by != current_user.id:
            return jsonify({
                "success": False,
                "message": "Access denied"
            }), 403

        if order.status == "Cancelled":
            return jsonify({
                "success": False,
                "message": "Order is already cancelled"
            }), 400

        if order.status == "Confirmed":

            items = SalesOrderItem.query.filter_by(
                sales_order_id=order.id
            ).order_by(
                SalesOrderItem.product_id
            ).all()

            for item in items:

                product = Product.query.filter_by(
                    id=item.product_id
                ).with_for_update().first()

                if not product:
                    raise ValueError("Product not found")

                product.stock_quantity += item.quantity

                movement = StockMovement(
                    product_id=product.id,
                    movement_type="IN",
                    quantity_change=item.quantity,
                    order_id=order.id,
                    reason="Sales order cancelled - stock restored",
                    created_by=current_user.id
                )

                db.session.add(movement)

        order.status = "Cancelled"

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Order cancelled successfully",
            "order_id": order.id,
            "status": order.status
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Unable to cancel order"
        }), 500