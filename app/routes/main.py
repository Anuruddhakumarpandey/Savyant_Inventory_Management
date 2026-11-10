from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.routes.decorators import role_required

main = Blueprint("main", __name__)


@main.route("/")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        user=current_user
    )


@main.route("/admin")
@login_required
@role_required("Admin")
def admin_dashboard():
    return "Admin access granted successfully!"