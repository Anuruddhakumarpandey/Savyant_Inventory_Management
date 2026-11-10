from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from app import db
from app.models import (
    Customer,
    Product,
    SalesOrder,
    SalesOrderItem,
    StockMovement
)
from app.routes.decorators import role_required


reports = Blueprint("reports", __name__)


# Reports Dashboard
@reports.route("/reports")
@login_required
@role_required("Admin")
def reports_dashboard():

    return render_template("reports.html")
# Customer Sales Summary
# Customer Sales Summary
@reports.route("/reports/customer-sales")
@login_required
@role_required("Admin")
def customer_sales_report():

    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")

    conditions = [
        SalesOrder.customer_id == Customer.id,
        SalesOrder.status == "Confirmed"
    ]

    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            conditions.append(SalesOrder.order_date >= start)
        except ValueError:
            start_date = ""

    if end_date:
        try:
            end = datetime.strptime(
                end_date, "%Y-%m-%d"
            ) + timedelta(days=1)

            conditions.append(SalesOrder.order_date < end)
        except ValueError:
            end_date = ""

    query = db.session.query(
        Customer.id,
        Customer.name,
        Customer.email,
        func.count(
            func.distinct(SalesOrder.id)
        ).label("total_orders"),
        func.coalesce(
            func.sum(SalesOrder.grand_total), 0
        ).label("total_sales")
    ).outerjoin(
        SalesOrder,
        and_(*conditions)
    )

    customers = query.group_by(
        Customer.id,
        Customer.name,
        Customer.email
    ).order_by(
        Customer.name
    ).all()

    return render_template(
        "reports_customer_sales.html",
        customers=customers,
        start_date=start_date,
        end_date=end_date
    )


# Product Sales Summary

# Product Sales Summary
@reports.route("/reports/product-sales")
@login_required
@role_required("Admin")
def product_sales_report():




    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")

    conditions = [
        SalesOrder.id == SalesOrderItem.sales_order_id,
        SalesOrder.status == "Confirmed"
    ]

    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            conditions.append(SalesOrder.order_date >= start)
        except ValueError:
            start_date = ""

    if end_date:
        try:
            end = datetime.strptime(
                end_date, "%Y-%m-%d"
            ) + timedelta(days=1)

            conditions.append(SalesOrder.order_date < end)
        except ValueError:
            end_date = ""

    query = db.session.query(
        Product.id,
        Product.product_code,
        Product.name,
        func.coalesce(
            func.sum(
                db.case(
                    (SalesOrder.id.isnot(None), SalesOrderItem.quantity),
                    else_=0
                )
            ), 0
        ).label("total_quantity"),
        func.coalesce(
            func.sum(
                db.case(
                    (SalesOrder.id.isnot(None), SalesOrderItem.amount),
                    else_=0
                )
            ), 0
        ).label("total_sales")
    ).outerjoin(
        SalesOrderItem,
        SalesOrderItem.product_id == Product.id
    ).outerjoin(
        SalesOrder,
        and_(*conditions)
    )

    products = query.group_by(
        Product.id,
        Product.product_code,
        Product.name
    ).order_by(Product.name).all()

    return render_template(
        "reports_product_sales.html",
        products=products,
        start_date=start_date,
        end_date=end_date
    )


# Low Stock Report
@reports.route("/reports/low-stock")
@login_required
@role_required("Admin")
def low_stock_report():

    threshold = request.args.get("threshold", "5")

    try:
        threshold = int(threshold)
        if threshold < 0:
            threshold = 5
    except ValueError:
        threshold = 5

    products = Product.query.filter(
        Product.stock_quantity <= threshold
    ).order_by(
        Product.stock_quantity.asc()
    ).all()

    return render_template(
        "reports_low_stock.html",
        products=products,
        threshold=threshold
    )




