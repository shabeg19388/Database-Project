import os
from dotenv import load_dotenv
from openai import OpenAI
import mysql.connector
load_dotenv()

GeminiClient = OpenAI(api_key = os.environ['GEMINI_API_KEY'], base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
GPTClient = OpenAI(api_key = os.environ['OPEN_API_KEY'])


sys_message = """Give the SQL query needed to resolve a user input. There is no need for explanation or anything just return the query compatible with mySQL. 
                The database is a Brazilian e-commerce database from O-List (in English). Only return the SQL query given the user input.
                The schema for the database is:
                    "customers(customer_id [PK], customer_unique_id, zip_code [FK: geolocation.zip_code], city, state): Has customer id and address information. 

                    orders(order_id [PK], customer_id [FK: customers.customer_id], order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date): Has order information including customer, status of order, purchase time, approval time, delivery to carrier, delivery to customer, and estimated delivery date to customer.

                    order_payments(order_id [FK: orders.order_id], payment_sequential, payment_type, payment_installments, payment_value): Has payment information for each order including installments and multiple payment methods (payment_sequential).

                    order_reviews(review_id [PK], order_id [FK: orders.order_id], review_score, review_comment_title, review_comment_message, review_creation_date, review_answer_timestamp): Has reviews for each order including score, title, message, date and answer from seller timestamp.

                    geolocation(zip_code [PK], lat, lang, city, state): Has location information for each zip code.

                    product_category_name_translation(category_name [PK], category_name_english): Has translation for category from portugese to english.

                    products(product_id [PK], category_name [FK: product_category_name_translation.category_name], name_length, description_length, photo_qty, weight_g, length_cm, height_cm, width_cm): Has product information including category in portugese, product name length, product description length, number of photos, weight of item and dimensions of item.

                    sellers(seller_id [PK], zip_code [FK: geolocation.zip_code], city, state): Has inforation on seller including address information.

                    order_items(order_id [FK: orders.order_id], order_item_id [PK], product_id [FK: products.product_id], 
                    seller_id [FK: sellers.seller_id], shipping_limit_date, price, freight_value): Has item information for each order including item number, product id, seller id, limit date for seller to hand over item to carrier, item price and item freight value item (if an order has more than one item the freight value is splitted between items)."   


                If you think that the user input is outside the scope of this schema then throw an error out of scope. 
                Convert the user input into an executable SQL query for the given database without any explanation.

                Return the resulting query in compact SQL.
                """

def getGPTcompletion(query : str)  -> str:
    completion = GPTClient.chat.completions.create(model = 'gpt-4o-mini',
        messages = [
            {
                'role' : 'system',
                'content' : sys_message
            },
            {
            'role' : 'user',
            'content' : query
            }])
    
    return (completion.choices[0].message.content).replace('sql\n', '').replace('```','')
def getGeminicompletion(query : str)  -> str:
    completion = (GeminiClient.chat.completions.create(model = 'gemini-1.5-flash',
        messages = [
            {
                'role' : 'system',
                'content' : sys_message
            },
            {
            'role' : 'user',
            'content' : query
            }]).choices[0].message.content).replace('sql\n', '').replace('```','')
    return completion
# print(getGeminicompletion('Find the most popular product in March'))

# gptquery = getGPTcompletion('Who is the customer with the most payments')
# print(gptquery)
def fetchSingleSQLQuery(query):
    try:    
        sqlConnect = mysql.connector.connect(user='admin', password = os.environ['RDS_PASSWORD'], host=os.environ['RDS_HOST'], database = 'olist')
    except mysql.connector.Error as err:
        print(err)
        return [{}]
    else:
        
        cur = sqlConnect.cursor(dictionary = True, buffered = True)
        cur.execute(query)
        result = cur.fetchall()
        columns = cur.column_names
        cur.close()
        sqlConnect.close()
        return columns, result



# print(fetchSingleSQLQuery(gptquery))
union_msg = """
        You will be given either a union or an intersection SQL query and I would like you to reformat that query without any INTERSECTION OR UNION operations you can use any method such as JOIN to work around it (Only reforumulate if absolutely needed). The queries are from LLMs so you can even refomulate them to make more senese. 
        The schema for the database is:
                    CREATE TABLE customers (
                            customer_id VARCHAR(50) PRIMARY KEY,
                            customer_unique_id VARCHAR(50),
                            customer_zip_code_prefix CHAR(5),
                            customer_city VARCHAR(50),
                            customer_state CHAR(2),
                            FOREIGN KEY (customer_zip_code_prefix) REFERENCES geolocation(zip_code)
                    ): Has customer id and address information. 

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
                    ): Has order information including customer, status of order, purchase time, approval time, delivery to carrier, delivery to customer, and estimated delivery date to customer.

                    CREATE TABLE order_payments (
                        order_id VARCHAR(50),
                        payment_sequential SMALLINT,
                        payment_type VARCHAR(20),
                        payment_installments SMALLINT,
                        payment_value DOUBLE PRECISION,
                        FOREIGN KEY (order_id) REFERENCES orders(order_id)
                    ): Has payment information for each order including installments and multiple payment methods (payment_sequential).

                    CREATE TABLE order_reviews (
                        review_id VARCHAR(200) PRIMARY KEY,
                        order_id VARCHAR(200),
                        review_score SMALLINT,
                        review_comment_title TEXT,
                        review_comment_message TEXT,
                        review_creation_date VARCHAR(200),
                        review_answer_timestamp VARCHAR(200),
                        FOREIGN KEY (order_id) REFERENCES orders(order_id)
                    ): Has reviews for each order including score, title, message, date and answer from seller timestamp.

                    CREATE TABLE geolocation (
                        zip_code CHAR(5) PRIMARY KEY,
                        latitude DOUBLE PRECISION,
                        longitude DOUBLE PRECISION,
                        city VARCHAR(50),
                        state CHAR(2)
                    ): Has location information for each zip code.

                    CREATE TABLE product_category_name_translation (
                        category_name VARCHAR(50) PRIMARY KEY,
                        category_name_english VARCHAR(50)
                    ): Has translation for category from portugese to english.

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
                    ): Has product information including category in portugese, product name length, product description length, number of photos, weight of item and dimensions of item.

                    CREATE TABLE sellers (
                        seller_id VARCHAR(50) PRIMARY KEY,
                        zip_code CHAR(5),
                        city VARCHAR(50),
                        state CHAR(2),
                        FOREIGN KEY (zip_code) REFERENCES geolocation(zip_code)
                    ): Has information on seller including address information.

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
                    ): Has item information for each order including item number, product id, seller id, limit date for seller to hand over item to carrier, item price and item freight value item (if an order has more than one item the freight value is splitted between items)."   

                Convert the user input into an executable SQL query for the given database without any explanation.

                Return the resulting query in compact SQL without any intersections or union operations.

"""
def unionandIntersectionCompletion(query : str) -> str:
    completion = GPTClient.chat.completions.create(model = 'gpt-4o-mini',
        messages = [
            {
                'role' : 'system',
                'content' : union_msg
            },
            {
            'role' : 'user',
            'content' : query
            }])
    return (completion.choices[0].message.content).replace('sql\n', '').replace('```','')

print(unionandIntersectionCompletion("""(SELECT AVG(review_score) AS average_score FROM order_reviews WHERE review_comment_message IS NOT NULL;
) UNION (SELECT AVG(review_score) AS average_score
FROM order_reviews
WHERE review_comment_message IS NOT NULL;

)"""))