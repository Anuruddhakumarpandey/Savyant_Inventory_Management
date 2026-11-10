import csv
import io

from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import Product, StockMovement
from app.routes.decorators import role_required


csv_import = Blueprint("csv_import", __name__)


@csv_import.route("/products/import", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def import_products():

    if request.method == "POST":

        file = request.files.get("file")

        if not file or not file.filename.lower().endswith(".csv"):
            flash("Please upload a valid CSV file.", "danger")
            return redirect(url_for("csv_import.import_products"))

        try:
            content = file.read().decode("utf-8-sig")

            reader = csv.DictReader(io.StringIO(content))

            required_columns = {
                "product_code",
                "product_name",
                "category",
                "price",
                "stock_quantity",
                "status"
            }

            if not reader.fieldnames or not required_columns.issubset(
                set(reader.fieldnames)
            ):
                flash("CSV columns are missing or invalid.", "danger")
                return redirect(url_for("csv_import.import_products"))

            products_to_add = []
            errors = []
            seen_codes = set()

            for row_number, row in enumerate(reader, start=2):

                try:
                    if not row or not any(
                        value and value.strip()
                        for value in row.values()
                        if isinstance(value, str)
                    ):
                        continue

                    code = (row.get("product_code") or "").strip()
                    name = (row.get("product_name") or "").strip()
                    category = (row.get("category") or "").strip()
                    status = (row.get("status") or "").strip().lower()

                    if not code or not name:
                        raise ValueError(
                            "Product code and product name are required."
                        )

                    if code in seen_codes:
                        raise ValueError(
                            "Duplicate product code in CSV."
                        )

                    seen_codes.add(code)

                    if Product.query.filter_by(
                        product_code=code
                    ).first():
                        raise ValueError(
                            "Product code already exists in database."
                        )

                    price = Decimal(row["price"])
                    quantity = int(row["stock_quantity"])

                    if not price.is_finite() or price < 0:
                        raise ValueError(
                            "Price must be a valid non-negative number."
                        )

                    if quantity < 0:
                        raise ValueError(
                            "Stock quantity cannot be negative."
                        )

                    if status not in ("active", "inactive"):
                        raise ValueError(
                            "Status must be Active or Inactive."
                        )

                    products_to_add.append({
                        "product_code": code,
                        "name": name,
                        "category": category,
                        "price": price,
                        "stock_quantity": quantity,
                        "is_active": status == "active"
                    })

                except (
                    ValueError,
                    InvalidOperation,
                    KeyError,
                    TypeError
                ) as e:

                    errors.append(
                        f"Row {row_number}: {e}"
                    )

            if not products_to_add and not errors:
                errors.append("CSV file contains no product records.")

            if errors:

                for error in errors:
                    flash(error, "danger")

                flash(
                    "Import cancelled. No products were saved.",
                    "danger"
                )

                return redirect(
                    url_for("csv_import.import_products")
                )

            for data in products_to_add:

                product = Product(
                    product_code=data["product_code"],
                    name=data["name"],
                    category=data["category"],
                    price=data["price"],
                    stock_quantity=data["stock_quantity"],
                    is_active=data["is_active"]
                )

                db.session.add(product)
                db.session.flush()

                if data["stock_quantity"] > 0:

                    movement = StockMovement(
                        product_id=product.id,
                        movement_type="IN",
                        quantity_change=data["stock_quantity"],
                        reason="Opening stock from CSV import",
                        created_by=current_user.id
                    )

                    db.session.add(movement)

            db.session.commit()

            flash(
                f"{len(products_to_add)} products imported successfully.",
                "success"
            )

        except Exception as e:

            db.session.rollback()

            flash(f"Import failed: {e}", "danger")

        return redirect(
            url_for("csv_import.import_products")
        )

    return render_template("csv_import.html")