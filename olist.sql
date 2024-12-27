CREATE DATABASE IF NOT EXISTS olist;
USE olist;

SET FOREIGN_KEY_CHECKS = 0; 

DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS order_payments;
DROP TABLE IF EXISTS order_reviews;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS sellers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS product_category_name_translation;
DROP TABLE IF EXISTS geolocation;

SET FOREIGN_KEY_CHECKS = 1; 

CREATE TABLE geolocation (
    zip_code CHAR(5) PRIMARY KEY,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    city VARCHAR(50),
    state CHAR(2)
);

CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50),
    customer_zip_code_prefix CHAR(5),
    customer_city VARCHAR(50),
    customer_state CHAR(2),
    FOREIGN KEY (customer_zip_code_prefix) REFERENCES geolocation(zip_code)
);

CREATE TABLE sellers (
    seller_id VARCHAR(50) PRIMARY KEY,
    zip_code CHAR(5),
    city VARCHAR(50),
    state CHAR(2),
    FOREIGN KEY (zip_code) REFERENCES geolocation(zip_code)
);

CREATE TABLE product_category_name_translation (
    category_name VARCHAR(50) PRIMARY KEY,
    category_name_english VARCHAR(50)
);

CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_category_name VARCHAR(50),
    product_name_lenght INTEGER,
    product_description_lenght INTEGER,
    product_photos_qty INTEGER,
    product_weight_g INTEGER,
    product_length_cm INTEGER,
    product_height_cm INTEGER,
    product_width_cm INTEGER,
    FOREIGN KEY (product_category_name) REFERENCES product_category_name_translation(category_name)
);

CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    order_status VARCHAR(50),
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);


CREATE TABLE order_payments (
    order_id VARCHAR(50),
    payment_sequential SMALLINT,
    payment_type VARCHAR(20),
    payment_installments SMALLINT,
    payment_value DOUBLE PRECISION,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);


CREATE TABLE order_reviews (
    review_id VARCHAR(200) PRIMARY KEY,
    order_id VARCHAR(200),
    review_score SMALLINT,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date VARCHAR(200),
    review_answer_timestamp VARCHAR(200),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE order_items (
    order_id VARCHAR(50),
    order_item_id SMALLINT,
    product_id VARCHAR(50),
    seller_id VARCHAR(50),
    shipping_limit_date TIMESTAMP,
    price REAL,
    freight_value REAL,
    PRIMARY KEY (order_id, order_item_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
);

CREATE TEMPORARY TABLE temp_geolocation (
    zip_code CHAR(5),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    city VARCHAR(50),
    state CHAR(2)
);
LOAD DATA INFILE '/Users/shabeggill/Desktop/Olist/data/olist_geolocation_dataset.csv'
INTO TABLE temp_geolocation
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(zip_code, latitude, longitude, city, state);
SELECT * FROM temp_geolocation;
INSERT IGNORE INTO geolocation
SELECT DISTINCT * FROM temp_geolocation;
SELECT * FROM geolocation;
DROP TEMPORARY TABLE temp_geolocation;

CREATE TEMPORARY TABLE temp_customers (
    customer_id VARCHAR(50),
    customer_unique_id VARCHAR(50),
    customer_zip_code_prefix CHAR(5),
    customer_city VARCHAR(50),
    customer_state CHAR(2)
);
LOAD DATA INFILE '/Users/shabeggill/Desktop/Olist/data/olist_customers_dataset.csv'
INTO TABLE temp_customers
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state);
INSERT IGNORE INTO customers
SELECT DISTINCT * FROM temp_customers;
DROP TEMPORARY TABLE temp_customers;

CREATE TEMPORARY TABLE temp_sellers (
    seller_id VARCHAR(50),
    zip_code CHAR(5),
    city VARCHAR(50),
    state CHAR(2)
);
LOAD DATA INFILE '/Users/shabeggill/Desktop/Olist/data/olist_sellers_dataset.csv'
INTO TABLE temp_sellers
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(seller_id, zip_code, city, state);
SELECT * FROM temp_sellers;
INSERT IGNORE INTO sellers
SELECT DISTINCT * FROM temp_sellers;
DROP TEMPORARY TABLE temp_sellers;

CREATE TEMPORARY TABLE temp_product_category_name_translation (
    category_name VARCHAR(50),
    category_name_english VARCHAR(50)
);
LOAD DATA INFILE '/Users/shabeggill/Desktop/Olist/data/product_category_name_translation.csv'
INTO TABLE temp_product_category_name_translation
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(category_name, category_name_english);

INSERT IGNORE INTO product_category_name_translation
SELECT DISTINCT * FROM temp_product_category_name_translation;
DROP TEMPORARY TABLE temp_product_category_name_translation;


CREATE TEMPORARY TABLE temp_products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_category_name VARCHAR(50),
    product_name_lenght INTEGER,
    product_description_lenght INTEGER,
    product_photos_qty INTEGER,
    product_weight_g INTEGER,
    product_length_cm INTEGER,
    product_height_cm INTEGER,
    product_width_cm INTEGER
);
LOAD DATA INFILE '/Users/shabeggill/Desktop/Olist/data/olist_products_dataset.csv'
INTO TABLE temp_products
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(product_id, product_category_name, @product_name_lenght, @product_description_lenght, @product_photos_qty, @product_weight_g, @product_length_cm, @product_height_cm, @product_width_cm)
SET 
    product_name_lenght = IF(@product_name_lenght = '' OR @product_name_lenght IS NULL, NULL, @product_name_lenght),
    product_description_lenght = IF(@product_description_lenght = '' OR @product_description_lenght IS NULL, NULL, @product_description_lenght),
    product_photos_qty = IF(@product_photos_qty = '' OR @product_photos_qty IS NULL, NULL, @product_photos_qty),
    product_weight_g = IF(@product_weight_g = '' OR @product_weight_g IS NULL, NULL, @product_weight_g),
    product_length_cm = IF(@product_length_cm = '' OR @product_length_cm IS NULL, NULL, @product_length_cm),
    product_height_cm = IF(@product_height_cm = '' OR @product_height_cm IS NULL, NULL, @product_height_cm),
    product_width_cm = IF(@product_width_cm = '' OR @product_width_cm IS NULL, NULL, @product_width_cm);
INSERT IGNORE INTO products
SELECT DISTINCT * FROM temp_products;
DROP TEMPORARY TABLE temp_products;


CREATE TEMPORARY TABLE temp_orders (
    order_id VARCHAR(50),
    customer_id VARCHAR(50),
    order_status VARCHAR(50),
    order_purchase_timestamp VARCHAR(50),
    order_approved_at VARCHAR(50),
    order_delivered_carrier_date VARCHAR(50),
    order_delivered_customer_date VARCHAR(50),
    order_estimated_delivery_date VARCHAR(50)
);
LOAD DATA INFILE '/Users/shabeggill/Desktop/Olist/data/olist_orders_dataset.csv'
INTO TABLE temp_orders
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(order_id, customer_id, order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date);
INSERT IGNORE INTO orders
SELECT DISTINCT * FROM temp_orders;
DROP TEMPORARY TABLE temp_orders;

CREATE TEMPORARY TABLE temp_order_payments (
    order_id VARCHAR(50),
    payment_sequential SMALLINT,
    payment_type VARCHAR(20),
    payment_installments SMALLINT,
    payment_value DOUBLE PRECISION
);
LOAD DATA INFILE '/Users/shabeggill/Desktop/Olist/data/olist_order_payments_dataset.csv'
INTO TABLE temp_order_payments
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(order_id, payment_sequential, payment_type, payment_installments, payment_value);
INSERT IGNORE INTO order_payments
SELECT DISTINCT * FROM temp_order_payments;
DROP TEMPORARY TABLE temp_order_payments;
SET sql_mode = '';

CREATE TEMPORARY TABLE temp_order_reviews (
    review_id VARCHAR(200),
    order_id VARCHAR(200),
    review_score SMALLINT,
    review_comment_title TEXT NULL,
    review_comment_message TEXT NULL,
    review_creation_date VARCHAR(200),
    review_answer_timestamp VARCHAR(200)
);

LOAD DATA INFILE '/Users/shabeggill/Desktop/Olist/data/olist_order_reviews_dataset.csv'
INTO TABLE temp_order_reviews
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    review_id,
    order_id,
    review_score,
    @review_comment_title,
    @review_comment_message,
    @review_creation_date,
    @review_answer_timestamp,
    @dummy 
)
SET 
    review_comment_title = IF(@review_comment_title = '', NULL, @review_comment_title),
    review_comment_message = IF(@review_comment_message = '', NULL, @review_comment_message),
    review_creation_date = IF(@review_creation_date REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$', 
                              STR_TO_DATE(@review_creation_date, '%Y-%m-%d %H:%i:%s'), NULL),
    review_answer_timestamp = IF(@review_answer_timestamp REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$', 
                                 STR_TO_DATE(@review_answer_timestamp, '%Y-%m-%d %H:%i:%s'), NULL);

INSERT IGNORE INTO order_reviews (
    review_id, 
    order_id, 
    review_score, 
    review_comment_title, 
    review_comment_message, 
    review_creation_date, 
    review_answer_timestamp
)
SELECT DISTINCT 
    review_id, 
    order_id, 
    review_score, 
    review_comment_title, 
    review_comment_message, 
    review_creation_date, 
    review_answer_timestamp
FROM temp_order_reviews;

DROP TEMPORARY TABLE temp_order_reviews;


SHOW VARIABLES LIKE 'secure_file_priv';



SET SQL_SAFE_UPDATES = 0;
CREATE TEMPORARY TABLE temp_order_items (
    order_id VARCHAR(50),
    order_item_id SMALLINT,
    product_id VARCHAR(50),
    seller_id VARCHAR(50),
    shipping_limit_date DATETIME, 
    price REAL,
    freight_value REAL,
    PRIMARY KEY (order_id, order_item_id) 
);

LOAD DATA INFILE '/Users/shabeggill/Desktop/Olist/data/olist_order_items_dataset.csv'
INTO TABLE temp_order_items
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(order_id, order_item_id, product_id, seller_id, @shipping_limit_date, price, freight_value)
SET shipping_limit_date = IF(STR_TO_DATE(@shipping_limit_date, '%Y-%m-%d %H:%i:%s'), 
                             STR_TO_DATE(@shipping_limit_date, '%Y-%m-%d %H:%i:%s'), 
                             NULL);

DELETE FROM temp_order_items
WHERE product_id NOT IN (SELECT product_id FROM products)
   OR order_id NOT IN (SELECT order_id FROM orders)
   OR seller_id NOT IN (SELECT seller_id FROM sellers);
INSERT INTO order_items
SELECT * FROM temp_order_items;

DROP TEMPORARY TABLE temp_order_items;

SET SQL_SAFE_UPDATES = 1;
