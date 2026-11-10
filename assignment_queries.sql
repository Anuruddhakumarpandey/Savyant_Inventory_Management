-- 1. Top 3 Customers by Confirmed Sales

SELECT
    c.id,
    c.name,
    SUM(so.grand_total) AS total_sales
FROM customers c
JOIN sales_orders so
    ON c.id = so.customer_id
WHERE so.status = 'Confirmed'
GROUP BY c.id, c.name
ORDER BY total_sales DESC
LIMIT 3;


-- 2. Top 3 Products by Confirmed Quantity Sold

SELECT
    p.id,
    p.product_code,
    p.name,
    SUM(soi.quantity) AS total_quantity_sold
FROM products p
JOIN sales_order_items soi
    ON p.id = soi.product_id
JOIN sales_orders so
    ON soi.sales_order_id = so.id
WHERE so.status = 'Confirmed'
GROUP BY p.id, p.product_code, p.name
ORDER BY total_quantity_sold DESC
LIMIT 3;


-- 3. Customers Who Never Placed an Order

SELECT
    c.id,
    c.name,
    c.email
FROM customers c
WHERE NOT EXISTS (
    SELECT 1
    FROM sales_orders so
    WHERE so.customer_id = c.id
);


-- 4. Month-wise Confirmed Sales Total

SELECT
    DATE_FORMAT(order_date, '%Y-%m') AS sales_month,
    SUM(grand_total) AS total_sales
FROM sales_orders
WHERE status = 'Confirmed'
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY sales_month;


-- 5. Products with Stock Below Threshold

SET @low_stock_threshold = 5;

SELECT
    id,
    product_code,
    name,
    stock_quantity
FROM products
WHERE stock_quantity < @low_stock_threshold
ORDER BY stock_quantity ASC;