CREATE DATABASE IF NOT EXISTS sales_analysis;
USE sales_analysis;

CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    UNIQUE KEY uq_product_name_category (product_name, category)
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    sale_date DATE NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    region VARCHAR(100) NOT NULL,
    import_hash CHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_sales_import_hash (import_hash),
    CONSTRAINT fk_sales_product FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);
