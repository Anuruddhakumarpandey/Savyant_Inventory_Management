# Inventory Management System

A Flask-based Inventory Management System developed using Python, Flask, MySQL, HTML, CSS, and JavaScript.

## 1. Project Overview

This application helps manage products, customers, inventory, and sales orders. It provides role-based access for Admin and Sales Users.

## 2. Technologies Used

- Python
- Flask
- MySQL
- Flask-SQLAlchemy
- Flask-Login
- Flask-Bcrypt
- Flask-Migrate
- HTML
- CSS
- JavaScript
- Bootstrap
- Pytest

## 3. Main Features

### User Management
- Admin and Sales User roles.
- Secure password hashing.
- Login authentication.

### Customer Management
- Add and manage customers.
- Search and filter customers.
- Activate and deactivate customers.

### Product Management
- Add and manage products.
- Product search and category filtering.
- Product activation and deactivation.
- Product price and stock validation.

### Inventory Management
- Stock IN and OUT adjustments.
- Stock movement history.
- Prevention of negative stock.

### Sales Order Management
- Create orders with multiple products.
- Automatic subtotal and discount calculation.
- Draft, Confirmed, and Cancelled order statuses.
- Automatic stock deduction on confirmation.
- Stock restoration on cancellation.
- Sales User order ownership restrictions.

### Reports
- Dashboard.
- Customer Sales Summary.
- Product Sales Summary.
- Low Stock Report.
- Stock Movement History.

### CSV Import
- Bulk product import using CSV.
- Validation for duplicate product codes.
- Price, quantity, and status validation.
- All-or-nothing import handling.

### REST API
- Retrieve active products.
- Create sales orders.
- Retrieve order details.
- Confirm and cancel orders.
- Authentication and ownership checks.

## 4. Project Structure

```text
savyant_inventory/
│
├── app/
│   ├── routes/
│   ├── static/
│   ├── templates/
│   ├── __init__.py
│   ├── calculations.py
│   └── models.py
│
├── tests/
│   └── test_calculations.py
│
├── .env
├── .env.example
├── AI_USAGE.md
├── assignment_queries.sql
├── config.py
├── create_admin.py
├── create_sales_user.py
├── invalid_sample_products.csv
├── sample_products.csv
├── requirements.txt
├── run.py
├── schema.sql
└── README.md
```

## 5. Installation and Setup

### Step 1: Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd savyant_inventory
```

### Step 2: Create virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\Activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure environment variables

Create a `.env` file using `.env.example` as a reference.

Configure:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=mysql+pymysql://username:password@localhost/savyant_inventory
```

Use your own MySQL credentials.

### Step 5: Create MySQL database

```sql
CREATE DATABASE savyant_inventory;
```

Import the database schema:

```bash
mysql -u root -p savyant_inventory < schema.sql
```

### Step 6: Create users

Run the user creation scripts:

```bash
python create_admin.py
python create_sales_user.py
```

Follow the prompts provided by the scripts.

### Step 7: Run the application

```bash
python run.py
```

Open the application in your browser:

```text
http://127.0.0.1:5000
```

## 6. REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/products` | Retrieve active products |
| POST | `/api/orders` | Create a sales order |
| GET | `/api/orders/<id>` | Retrieve order details |
| POST | `/api/orders/<id>/confirm` | Confirm an order |
| POST | `/api/orders/<id>/cancel` | Cancel an order |

API access requires authentication.

## 7. SQL Assignment Queries

The `assignment_queries.sql` file contains five queries:

1. Top 3 customers by confirmed sales.
2. Top 3 products by confirmed quantity sold.
3. Customers who never placed an order.
4. Month-wise confirmed sales.
5. Products with stock below a specified threshold.

## 8. Automated Testing

Run the tests using:

```bash
python -m pytest -v
```

The calculation module is tested for:

- Valid calculations.
- Empty and missing items.
- Missing quantity and rate.
- Zero and negative quantities.
- Negative and invalid rates.

## 9. Sample CSV Files

- `sample_products.csv` – Valid sample product data.
- `invalid_sample_products.csv` – Invalid data for validation testing.

## 10. AI Usage Disclosure

Refer to `AI_USAGE.md` for details about AI tools used during development and the areas where assistance was taken.

## 11. Security Notes

- Credentials are stored in environment variables.
- Passwords are hashed.
- Role-based authorization is implemented.
- Sales Users can access only their own sales orders.
- Stock cannot become negative through the implemented inventory and order operations.

## 12. Author

**Anuruddha Kumar Pandey**

Python Full Stack Developer