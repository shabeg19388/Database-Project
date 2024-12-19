CREATE DATABASE IF NOT EXISTS olist;
USE olist;

/* Step 1: Drop dependent tables first */
SET FOREIGN_KEY_CHECKS = 0; -- Temporarily disable foreign key constraints

/* Drop existing tables */
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS order_payments;
DROP TABLE IF EXISTS order_reviews;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS sellers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS product_category_name_translation;
DROP TABLE IF EXISTS geolocation;

SET FOREIGN_KEY_CHECKS = 1; -- Re-enable foreign key constraints

/* Step 1: Create geolocation table */
CREATE TABLE geolocation (
    zip_code CHAR(5) PRIMARY KEY,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    city VARCHAR(50),
    state CHAR(2)
);

/* Step 2: Create customers table */
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50),
    customer_zip_code_prefix CHAR(5),
    customer_city VARCHAR(50),
    customer_state CHAR(2),
    FOREIGN KEY (customer_zip_code_prefix) REFERENCES geolocation(zip_code)
);

/* Step 3: Create sellers table */
CREATE TABLE sellers (
    seller_id VARCHAR(50) PRIMARY KEY,
    zip_code CHAR(5),
    city VARCHAR(50),
    state CHAR(2),
    FOREIGN KEY (zip_code) REFERENCES geolocation(zip_code)
);

/* Step 4: Create product_category_name_translation table */
CREATE TABLE product_category_name_translation (
    category_name VARCHAR(50) PRIMARY KEY,
    category_name_english VARCHAR(50)
);

/* Step 5: Create products table */
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

/* Step 6: Create orders table */
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

/* Step 7: Create order_payments table */
CREATE TABLE order_payments (
    order_id VARCHAR(50),
    payment_sequential SMALLINT,
    payment_type VARCHAR(20),
    payment_installments SMALLINT,
    payment_value DOUBLE PRECISION,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

/* Step 8: Create order_reviews table */
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

/* Step 9: Create order_items table */
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

/* Load data into geolocation table */
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
INSERT IGNORE INTO geolocation
SELECT DISTINCT * FROM temp_geolocation;
DROP TEMPORARY TABLE temp_geolocation;

/* Load data into customers table */
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
SELECT COUNT(* )FROM customers;

/* Repeat for remaining tables */

/* Load data into sellers */
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
INSERT IGNORE INTO sellers
SELECT DISTINCT * FROM temp_sellers;
DROP TEMPORARY TABLE temp_sellers;

/* Load data into product_category_name_translation */
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

/* Load data into products */
-- DROP TEMPORARY TABLE IF EXISTS temp_products;



-- Error Code: 1366. Incorrect integer value: '' for column 'product_name_lenght' at row 106
/* Load data into orders */
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
-- Error Code: 1292. Incorrect datetime value: '' for column 'order_delivered_carrier_date' at row 7

/* Load data into order_payments */
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

/* Load data into order_reviews */
-- Temporary table for order_reviews
-- Disable strict mode to allow for flexibility in handling bad data
SET sql_mode = '';

-- Create a temporary table with the same structure as the target table
CREATE TEMPORARY TABLE temp_order_reviews (
    review_id VARCHAR(200),
    order_id VARCHAR(200),
    review_score SMALLINT,
    review_comment_title TEXT NULL,
    review_comment_message TEXT NULL,
    review_creation_date DATETIME NULL,
    review_answer_timestamp DATETIME NULL
);

-- Load the data into the temporary table
LOAD DATA INFILE '/Users/shabeggill/Desktop/Olist/data/olist_order_reviews_dataset.csv'
INTO TABLE temp_order_reviews
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"' -- Handles fields optionally enclosed in double quotes
LINES TERMINATED BY '\n'
IGNORE 1 ROWS -- Skip the header row
(
    review_id,
    order_id,
    review_score,
    @review_comment_title, -- Handle empty values here
    @review_comment_message, -- Handle empty values here
    @review_creation_date,
    @review_answer_timestamp
)
SET 
    review_comment_title = IF(@review_comment_title = '', NULL, @review_comment_title), -- Replace empty strings with NULL
    review_comment_message = IF(@review_comment_message = '', NULL, @review_comment_message), -- Replace empty strings with NULL
    review_creation_date = IF(@review_creation_date REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$', 
                              STR_TO_DATE(@review_creation_date, '%Y-%m-%d %H:%i:%s'), NULL), -- Validate date format
    review_answer_timestamp = IF(@review_answer_timestamp REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$', 
                                 STR_TO_DATE(@review_answer_timestamp, '%Y-%m-%d %H:%i:%s'), NULL); -- Validate date format

-- Insert the cleaned data from the temporary table into the main table
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

-- Drop the temporary table
DROP TEMPORARY TABLE temp_order_reviews;

-- Re-enable strict mode if necessary
SET sql_mode = 'STRICT_TRANS_TABLES';



-- Temporary table for order_items
CREATE TEMPORARY TABLE temp_order_items (
    order_id VARCHAR(50),
    order_item_id SMALLINT,
    product_id VARCHAR(50),
    seller_id VARCHAR(50),
    shipping_limit_date TIMESTAMP,
    price REAL,
    freight_value REAL
);

LOAD DATA INFILE '/Users/shabeggill/Desktop/Olist/data/olist_order_items_dataset.csv'
INTO TABLE temp_order_items
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(order_id, order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value)
SET shipping_limit_date = STR_TO_DATE(@shipping_limit_date, '%Y-%m-%d %H:%i:%s');

INSERT IGNORE INTO order_items
SELECT DISTINCT * FROM temp_order_items;
DROP TEMPORARY TABLE temp_order_items;



SHOW VARIABLES LIKE 'secure_file_priv';
SELECT COUNT(*) FROM order_reviews;
SELECT * FROM order_reviews;
-- SET FOREIGN_KEY_CHECKS = 1; -- Re-enable foreign key constraints-- 
