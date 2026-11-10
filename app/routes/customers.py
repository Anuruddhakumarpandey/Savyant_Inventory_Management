from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Customer
from app.routes.decorators import role_required

customers = Blueprint("customers", __name__)


@customers.route("/customers")
@login_required
@role_required("Admin")
def customer_list():

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    query = Customer.query

    if search:
        query = query.filter(
            db.or_(
                Customer.name.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%"),
                Customer.mobile.ilike(f"%{search}%"),
                Customer.city.ilike(f"%{search}%")
            )
        )

    if status == "active":
        query = query.filter_by(is_active=True)

    elif status == "inactive":
        query = query.filter_by(is_active=False)

    all_customers = query.order_by(
        Customer.id.desc()
    ).all()

    return render_template(
        "customers.html",
        customers=all_customers,
        search=search,
        status=status
    )


    return render_template(
    "customers.html",
    customers=all_customers,
    search=search,
    status=status
)





@customers.route("/customers/add", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def add_customer():

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        mobile = request.form.get("mobile", "").strip()
        city = request.form.get("city", "").strip()

        if not name:
            flash("Customer name is required.", "danger")
            return redirect(url_for("customers.add_customer"))

        customer = Customer(
            name=name,
            email=email or None,
            mobile=mobile or None,
            city=city or None
        )

        db.session.add(customer)
        db.session.commit()

        flash("Customer added successfully!", "success")

        return redirect(url_for("customers.customer_list"))

    return render_template("customer_form.html")




@customers.route("/customers/edit/<int:customer_id>", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def edit_customer(customer_id):

    customer = db.session.get(Customer, customer_id)

    if customer is None:
        return "Customer not found", 404

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        mobile = request.form.get("mobile", "").strip()
        city = request.form.get("city", "").strip()

        if not name:
            flash("Customer name is required.", "danger")
            return redirect(
                url_for("customers.edit_customer", customer_id=customer.id)
            )

        customer.name = name
        customer.email = email or None
        customer.mobile = mobile or None
        customer.city = city or None

        db.session.commit()

        flash("Customer updated successfully!", "success")

        return redirect(url_for("customers.customer_list"))

    return render_template("customer_form.html", customer=customer)


@customers.route("/customers/deactivate/<int:customer_id>", methods=["POST"])
@login_required
@role_required("Admin")
def deactivate_customer(customer_id):

    customer = db.session.get(Customer, customer_id)

    if customer is None:
        return "Customer not found", 404

    customer.is_active = False

    db.session.commit()

    flash("Customer deactivated successfully!", "success")

    return redirect(url_for("customers.customer_list"))


@customers.route("/customers/reactivate/<int:customer_id>", methods=["POST"])
@login_required
@role_required("Admin")
def reactivate_customer(customer_id):

    customer = db.session.get(Customer, customer_id)

    if customer is None:
        return "Customer not found", 404

    customer.is_active = True

    db.session.commit()

    flash("Customer reactivated successfully!", "success")

    return redirect(url_for("customers.customer_list"))