CREATE DATABASE IF NOT EXISTS savyant_inventory;
USE savyant_inventory;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    CONSTRAINT check_user_role
        CHECK (role IN ('Admin', 'Sales User'))
);

CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120),
    mobile VARCHAR(15),
    city VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    INDEX idx_customer_name (name)
);

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT check_product_price CHECK (price >= 0),
    CONSTRAINT check_stock_quantity CHECK (stock_quantity >= 0),
    INDEX idx_product_name (name)
);

CREATE TABLE IF NOT EXISTS sales_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    customer_id INT NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'Draft',
    discount_percent DECIMAL(5,2) NOT NULL DEFAULT 0,
    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0,
    discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    grand_total DECIMAL(12,2) NOT NULL DEFAULT 0,
    created_by INT NOT NULL,

    CONSTRAINT check_order_status
        CHECK (status IN ('Draft', 'Confirmed', 'Cancelled')),

    CONSTRAINT check_discount_percent
        CHECK (discount_percent BETWEEN 0 AND 20),

    FOREIGN KEY (customer_id)
        REFERENCES customers(id) ON DELETE RESTRICT,

    FOREIGN KEY (created_by)
        REFERENCES users(id) ON DELETE RESTRICT,

    INDEX idx_sales_customer (customer_id)
);

CREATE TABLE IF NOT EXISTS sales_order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sales_order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    rate DECIMAL(10,2) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,

    CONSTRAINT unique_product_per_order
        UNIQUE (sales_order_id, product_id),

    CONSTRAINT check_quantity_positive
        CHECK (quantity > 0),

    CONSTRAINT check_order_item_amount
        CHECK (rate >= 0 AND amount >= 0),

    FOREIGN KEY (sales_order_id)
        REFERENCES sales_orders(id) ON DELETE RESTRICT,

    FOREIGN KEY (product_id)
        REFERENCES products(id) ON DELETE RESTRICT,

    INDEX idx_item_order (sales_order_id),
    INDEX idx_item_product (product_id)
);

CREATE TABLE IF NOT EXISTS stock_movements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    movement_type VARCHAR(20) NOT NULL,
    quantity_change INT NOT NULL,
    order_id INT,
    reason VARCHAR(255),
    created_by INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id)
        REFERENCES products(id) ON DELETE RESTRICT,

    FOREIGN KEY (order_id)
        REFERENCES sales_orders(id) ON DELETE RESTRICT,

    FOREIGN KEY (created_by)
        REFERENCES users(id) ON DELETE RESTRICT,

    INDEX idx_stock_product (product_id),
    INDEX idx_stock_order (order_id)
);