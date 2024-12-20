from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import mysql.connector


load_dotenv()

app = Flask(__name__)
CORS(app, origins = ['http://localhost:3000'])
GPTClient = OpenAI(api_key = os.environ['OPEN_API_KEY'])
GeminiClient = OpenAI(api_key = os.environ['GEMINI_API_KEY'], base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

#have to fix schema and add examples also can add an example row from each table. Also fix schema in frontend.
sys_message = """Give the SQL query needed to resolve a user input. There is no need for explanation or anything just return the query compatible with mySQL. 
                The database is a Brazilian e-commerce database from O-List (in English). Only return the SQL query given the user input.
               
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

                    CCREATE TABLE geolocation (
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

                Here is an instance of each table: 

                geolocation(01001, -23.551426655288804, -46.63407394670785, sao paulo, SP) 

                product_category_name_translation(agro_industria_e_comercio, agro_industry_and_commerce) 

                products(00066f42aeeb9f3007548bb9d3f33c38, perfumaria, 53, 596, 6, 300, 20, 16, 16) 

                sellers(0015a82c2db000af6aaaf3ae2ecb0532, 09080, santo andre, SP) 

                customers (00012a2ce6f8dcda20d059ce98491703, 248ffe10d632bebe4f7267f1f44844c9, 06273, osasco, SP) 

                orders(00010242fe8c5a6d1ba2dd792cb16214, 3ce436f183e68e07877b285a838db11a, delivered, 2017-09-13 08:59:02, 2017-09-13 09:45:35, 2017-09-19 18:34:16, 2017-09-20 23:43:48, 2017-09-29 00:00:00) 

                order_reviews(00020c7512a52e92212f12d3e37513c0, e28abf2eb2f1fbcbdc2dd0cd9a561671, 5, Entrega rápida!, A entrega foi super rápida e o pendente é lindo! Igual a foto mesmo!, 2018-04-25 00:00:00, 2018-04-26 14:55:36) 

                order_payments(00010242fe8c5a6d1ba2dd792cb16214, 1, credit_card, 2, 72.19) 

                order_items(00010242fe8c5a6d1ba2dd792cb16214, 1, 4244733e06e7ecb4970a6e2683c13e61, 48436dade18ac8b2bce089ec2a041202, 2017-09-19 09:45:35, 58.9, 13.29) 

                For reference here are few English queries with their corresponding SQL code for the olist e-commerce database.
                
                1. List the customers who live in the city, Sao Paulo, and have reviewed a product and given it a score of 5:
                        SELECT DISTINCT c.customer_id
                        FROM customers c
                        JOIN orders o ON c.customer_id = o.customer_id
                        JOIN order_reviews r ON o.order_id = r.order_id
                        WHERE c.customer_city = 'Sao Paulo' AND r.review_score = 5;

                2. Give me the sellers along with their products where the customers gave an average rating of 4 to the product:

                        SELECT s.seller_id,p.product_id,AVG(r.review_score) AS avg_rating
                        FROM sellers s
                        JOIN order_items oi ON s.seller_id = oi.seller_id
                        JOIN products p ON oi.product_id = p.product_id
                        JOIN orders o ON oi.order_id = o.order_id
                        JOIN order_reviews r ON o.order_id = r.order_id
                        GROUP BY s.seller_id, p.product_id
                        HAVING AVG(r.review_score) = 4;

                3. List all sellers, their products, and the number of 5-star reviews for each product, along with the customers who purchased the product, their payment types, and total payments for these orders:

                        SELECT s.seller_id,p.product_id,p.product_category_name,COUNT(r.review_id) AS five_star_reviews_count,c.customer_id,op.payment_type,SUM(op.payment_value) AS total_payment
                        FROM sellers s
                        JOIN order_items oi ON s.seller_id = oi.seller_id
                        JOIN products p ON oi.product_id = p.product_id
                        JOIN orders o ON oi.order_id = o.order_id
                        JOIN customers c ON o.customer_id = c.customer_id
                        JOIN order_reviews r ON o.order_id = r.order_id
                        JOIN order_payments op ON o.order_id = op.order_id
                        WHERE r.review_score = 5
                        GROUP BY s.seller_id, p.product_id, p.product_category_name, c.customer_id, op.payment_type
                        ORDER BY five_star_reviews_count DESC, total_payment DESC;
                    
                4. List only the sellers who have delivered an order more than 3 days late to a customer.

                        SELECT DISTINCT s.seller_id
                        FROM sellers s
                        JOIN order_items oi ON s.seller_id = oi.seller_id
                        JOIN orders o ON oi.order_id = o.order_id
                        WHERE o.order_delivered_customer_date > o.order_estimated_delivery_date + INTERVAL 3 DAY;
                                        
                NOTE: All attribute names and table names are in lower case. Make sure not to capitalize them when writing SQL queries.
                Convert the user input into an executable SQL query for the given database without any explanation.

                Return the resulting query in compact SQL.
                """
def getGPTCompletion(query : str)  -> str:
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

def getGeminiCompletion(query : str, columns : list)  -> str:
    completion_base = GeminiClient.chat.completions.create(model = 'gemini-1.5-flash',
        messages = [
            {
                'role' : 'system',
                'content' : sys_message
            },
            {
            'role' : 'user',
            'content' : f'{query}'
            }])
    completion_name = GeminiClient.chat.completions.create(model = 'gemini-1.5-flash',
        messages = [
            {
                'role' : 'system',
                'content' : sys_message
            },
            {
            'role' : 'user',
            'content' : f'{query} with column output {columns}'
            }])
    
    completion_num = GeminiClient.chat.completions.create(model = 'gemini-1.5-flash',
        messages = [
            {
                'role' : 'system',
                'content' : sys_message
            },
            {
            'role' : 'user',
            'content' : f'I want this English query in SQL: {query} with {len(columns)} number of columns'
            }])
    
    GeminiQuery, NumQuery, NameQuery = (completion_base.choices[0].message.content).replace('sql\n', '').replace('```',''), (completion_num.choices[0].message.content).replace('sql\n', '').replace('```',''), (completion_name.choices[0].message.content).replace('sql\n', '').replace('```','')
    return GeminiQuery, NumQuery, NameQuery

intersection_msg = """
        You will be given an intersection SQL query of two SQL queries from LLMs and I would like you to reformat that query without any INTERSECTION operations you can use any method such as JOIN or EXISTS to work around the operation. Do not change the meaning of the query. Do not output any uneccessary attributes except the ones mention in the query.
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

                    CCREATE TABLE geolocation (
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

                Here is an instance of each table: 
                geolocation(01001, -23.551426655288804, -46.63407394670785, sao paulo, SP) 

                product_category_name_translation(agro_industria_e_comercio, agro_industry_and_commerce) 

                products(00066f42aeeb9f3007548bb9d3f33c38, perfumaria, 53, 596, 6, 300, 20, 16, 16) 

                sellers(0015a82c2db000af6aaaf3ae2ecb0532, 09080, santo andre, SP) 

                customers (00012a2ce6f8dcda20d059ce98491703, 248ffe10d632bebe4f7267f1f44844c9, 06273, osasco, SP) 

                orders(00010242fe8c5a6d1ba2dd792cb16214, 3ce436f183e68e07877b285a838db11a, delivered, 2017-09-13 08:59:02, 2017-09-13 09:45:35, 2017-09-19 18:34:16, 2017-09-20 23:43:48, 2017-09-29 00:00:00) 

                order_reviews(00020c7512a52e92212f12d3e37513c0, e28abf2eb2f1fbcbdc2dd0cd9a561671, 5, Entrega rápida!, A entrega foi super rápida e o pendente é lindo! Igual a foto mesmo!, 2018-04-25 00:00:00, 2018-04-26 14:55:36) 

                order_payments(00010242fe8c5a6d1ba2dd792cb16214, 1, credit_card, 2, 72.19) 

                order_items(00010242fe8c5a6d1ba2dd792cb16214, 1, 4244733e06e7ecb4970a6e2683c13e61, 48436dade18ac8b2bce089ec2a041202, 2017-09-19 09:45:35, 58.9, 13.29) 

                NOTE: All attribute names and table names are in lower case. Make sure not to capitalize them when writing SQL queries.
                Convert the user input into an executable SQL query for the given database without any explanation.

                Return the resulting query in compact SQL without any intersections or union operations.

"""

def getIntersectionCompletion(query : str) -> str:
    completion = GPTClient.chat.completions.create(model = 'gpt-4o-mini',
        messages = [
            {
                'role' : 'system',
                'content' : intersection_msg
            },
            {
            'role' : 'user',
            'content' : query
            }])
    return (completion.choices[0].message.content).replace('sql\n', '').replace('```','')




def fetchSingleSQLQuery(query):
    try:    
        sqlConnect = mysql.connector.connect(user='admin', password = os.environ['RDS_PASSWORD'], host=os.environ['RDS_HOST'], database = 'olist')
    except mysql.connector.Error as err:
        print(err)
        return [], []
    else:
        cur = sqlConnect.cursor(dictionary = True, buffered = True)
        cur.execute(query)
        result = cur.fetchall()
        columns = cur.column_names
        cur.close()
        sqlConnect.close()
        return columns, result



def fetchMultipleSQLQueries(queries):
    try:    
        sqlConnect = mysql.connector.connect(user='admin', password = os.environ['RDS_PASSWORD'], host=os.environ['RDS_HOST'], database = 'olist')
    except mysql.connector.Error as err:
        print('Database Connection Failed')
        print(err)
        return []*5
    else:
        results = []
        cur = sqlConnect.cursor(dictionary = True, buffered = True)
        # i = 0
        for query in queries:
            try:
                # print(i)
                # i += 1
                cur.execute(query)
                results.append(cur.fetchall())
            except mysql.connector.Error as err:
                print(f'Failed on query: {query}')
                print(err)
                results.append([])

                

        cur.close()
        sqlConnect.close()
        return results




@app.post('/query')
def query():
    GPTQuery = getGPTCompletion(request.json['query'])
    #After querying the data we want to extract the column names and send it to the gemini query. Thinking about bias: We need to make sure that the prompt we are giving Gemini isn't too biased. My solution: We try all approaches have gemini come up with its own query, give the column names from gpt to gemini, give only the number of columns from gemini. For the intersection and union we can just use the query where we give the column names.
    
    col,gpt = fetchSingleSQLQuery(GPTQuery)

    GeminiQuery, NumQuery, NameQuery = getGeminiCompletion(request.json['query'], col )
    UnionQuery = f'({GPTQuery.replace(';', '')}) UNION ({NameQuery.replace(';', '')});'
    IntersectionQuery = f'({GPTQuery.replace(';', '')}) INTERSECTION ({NameQuery.replace(';', '')});'
    IntersectionQuery = getIntersectionCompletion(IntersectionQuery)
    queries = [GeminiQuery, NumQuery, NameQuery,  UnionQuery, IntersectionQuery]
    results = fetchMultipleSQLQueries(queries)
    gemini, gemini_num, gemini_name, intersection, union = results[0], results[1], results[2], results[3], results[4]
    
    response = {
        "GPTQuery" : GPTQuery,
        'gpt' : gpt,
        'GeminiQuery' : GeminiQuery,
        'gemini' : gemini,
        'NumQuery' : NumQuery,
        'gemini_num' : gemini_num,
        'NameQuery' : NameQuery,
        'gemini_name' : gemini_name,
        'IntersectionQuery' : IntersectionQuery,
        'intersection' : intersection,
        'UnionQuery' : UnionQuery,
        'union' : union
    }
    
    return jsonify(response)


@app.post('/test')
def test():
    print(request.json)
    gpt = [
  {
    "review_id": "b1f0fdd0-1a01-4e67-bd7c-3d5e0c3e3a5a",
    "order_id": "e481f51cbdc54678b7cc49136f2d6af7",
    "review_score": 5,
    "review_comment_title": "Excellent!",
    "review_comment_message": "The product exceeded my expectations.",
    "review_creation_date": "2024-12-01",
    "review_answer_timestamp": "2024-12-02T10:15:30"
  },
  {
    "review_id": "c2e0fdd1-2b02-5f68-ce8d-4e6f1d4f4b6b",
    "order_id": "f581g62dced65789c8dd59247g3e7bg8",
    "review_score": 4,
    "review_comment_title": "Very good",
    "review_comment_message": "Satisfied with the purchase.",
    "review_creation_date": "2024-12-03",
    "review_answer_timestamp": "2024-12-04T11:20:45"
  },
  {
    "review_id": "d3f1gde2-3c03-6g79-df9e-5f7g2e5g5c7c",
    "order_id": "g682h73efef76890d9ee60358h4f8ch9",
    "review_score": 3,
    "review_comment_title": "Average",
    "review_comment_message": "The product is okay, not great.",
    "review_creation_date": "2024-12-05",
    "review_answer_timestamp": "2024-12-06T12:25:50"
  },
  {
    "review_id": "e4g2hef3-4d04-7h8a-eg0f-6g8h3f6h6d8d",
    "order_id": "h783i84fgfg87901e0ff71469i5g9di0",
    "review_score": 2,
    "review_comment_title": "Not satisfied",
    "review_comment_message": "The product did not meet my expectations.",
    "review_creation_date": "2024-12-07",
    "review_answer_timestamp": "2024-12-08T13:30:55"
  },
  {
    "review_id": "f5h3igf4-5e05-8i9b-fh1g-7h9i4g7i7e9e",
    "order_id": "i894j95ghgh98012f1gg82570j6h0ej1",
    "review_score": 1,
    "review_comment_title": "Very disappointed",
    "review_comment_message": "The product was defective.",
    "review_creation_date": "2024-12-09",
    "review_answer_timestamp": "2024-12-10T14:35:00"
  },
  {
    "review_id": "g6i4jhf5-6f06-9j0c-gi2h-8i0j5h8j8f0f",
    "order_id": "j905k06hihi09123g2hh93681k7i1fk2",
    "review_score": 5,
    "review_comment_title": "Highly recommend",
    "review_comment_message": "Fantastic product and service.",
    "review_creation_date": "2024-12-11",
    "review_answer_timestamp": "2024-12-12T15:40:05"
  },
  {
    "review_id": "h7j5kig6-7g07-0k1d-hj3i-9j1k6i9k9g1g",
    "order_id": "k016l17ijij10234h3ii04792l8j2gl3",
    "review_score": 4,
    "review_comment_title": "Good value",
    "review_comment_message": "Worth the price.",
    "review_creation_date": "2024-12-13",
    "review_answer_timestamp": "2024-12-14T16:45:10"
  },
  {
    "review_id": "i8k6ljg7-8h08-1l2e-ik4j-0k2l7j0l0h2h",
    "order_id": "l127m28jkjk21345i4jj15803m9k3hm4",
    "review_score": 3,
    "review_comment_title": "It's okay",
    "review_comment_message": "The product is average.",
    "review_creation_date": "2024-12-15",
    "review_answer_timestamp": "2024-12-16T17:50:15"
  },
  {
    "review_id": "j9l7mkh8-9i09-2m3f-jl5k-1l3m8k1m1i3i",
    "order_id": "m238n39klkl32456j5kk26914n0l4in5",
    "review_score": 2,
    "review_comment_title": "Could be better",
    "review_comment_message": "Not what I expected.",
    "review_creation_date": "2024-12-17",
    "review_answer_timestamp": "2024-12-18T18:55:20"
  },
  {
    "review_id": "k0m8nli9-0j10-3n4g-km6l-2m4n9l2n2j4j",
    "order_id": "n349o40lmlm43567k6ll37025o1m5jo6",
    "review_score": 1,
    "review_comment_title": "Terrible experience",
    "review_comment_message": "The product arrived damaged.",
    "review_creation_date": "2024-12-19",
    "review_answer_timestamp": "2024-12-20T19:00:25"
  }
]*5

    gemini = [
        {
            "order_id": 101,
            "customer_id": 1,
            "order_status": "delivered",
            "order_purchase_timestamp": "2024-12-01 10:45:00",
            "order_approved_at": "2024-12-01 11:00:00",
            "order_delivered_carrier_date": "2024-12-03 14:30:00",
            "order_delivered_customer_date": "2024-12-05 16:00:00",
            "order_estimated_delivery_date": "2024-12-07 18:00:00"
        },
        {
            "order_id": 102,
            "customer_id": 2,
            "order_status": "shipped",
            "order_purchase_timestamp": "2024-12-02 09:15:00",
            "order_approved_at": "2024-12-02 09:45:00",
            "order_delivered_carrier_date": "Pending",
            "order_delivered_customer_date": "Pending",
            "order_estimated_delivery_date": "2024-12-10 18:00:00"
        }
    ]
    union = [
        {
            "order_id": 101,
            "payment_sequential": 1,
            "payment_type": "credit_card",
            "payment_installments": 3,
            "payment_value": 150.75
        },
        {
            "order_id": 102,
            "payment_sequential": 1,
            "payment_type": "boleto",
            "payment_installments": 1,
            "payment_value": 50.00
        }
    ]
    gemini_num = [
        {
            "order_id": 101,
            "payment_sequential": 1,
            "payment_type": "credit_card",
            "payment_installments": 3,
            "payment_value": 150.75
        },
        {
            "order_id": 102,
            "payment_sequential": 1,
            "payment_type": "boleto",
            "payment_installments": 1,
            "payment_value": 50.00
        }
    ]
    intersection = [
        {
            "review_id": 1001,
            "order_id": 101,
            "review_score": 5,
            "review_comment_title": "Excellent service!",
            "review_comment_message": "The product arrived on time and in perfect condition. Highly recommended!",
            "review_creation_date": "2024-12-06 08:30:00",
            "review_answer_timestamp": "2024-12-06 09:00:00"
        },
        {
            "review_id": 1002,
            "order_id": 102,
            "review_score": 4,
            "review_comment_title": "Good product",
            "review_comment_message": "The quality is good, but delivery took longer than expected.",
            "review_creation_date": "2024-12-11 10:00:00",
            "review_answer_timestamp": "2024-12-11 12:00:00"
        }
    ]
    
    gemini_name = [
        {
            "customer_id": 1,
            "customer_unique_id": "c1a1e1f1-4d2b-4632-bbbd-888f1c2a2d2e",
            "zip_code": "90210",
            "city": "Beverly Hills",
            "state": "CA"
        },
        {
            "customer_id": 2,
            "customer_unique_id": "a9b2c3d4-1234-5678-9101-1a2b3c4d5e6f",
            "zip_code": "10001",
            "city": "New York",
            "state": "NY"
        }
    ]*50
    response = {
        'gpt' : gpt,
        'gemini' : gemini,
        'union' : union,
        'intersection' : intersection,
        'gemini_name' : gemini_name,
        'gemini_num' : gemini_num,
        "GPTQuery" :  "SELECT c.customer_id, SUM(p.payment_value) AS total_spent\nFROM customers c\nJOIN orders o ON c.customer_id = o.customer_id\nJOIN order_payments p ON o.order_id = p.order_id\nGROUP BY c.customer_id\nORDER BY total_spent DESC\nLIMIT 100;\n",
        "GeminiQuery" : "SELECT\n  c.customer_unique_id\nFROM customers AS c\nJOIN orders AS o\n  ON c.customer_id = o.customer_id\nJOIN order_payments AS op\n  ON o.order_id = op.order_id\nGROUP BY\n  c.customer_unique_id\nORDER BY\n  SUM(op.payment_value) DESC\nLIMIT 100;\n\n",
        "NumQuery" : "SELECT c.customer_id, SUM(p.payment_value) AS total_spent\nFROM customers c\nJOIN orders o ON c.customer_id = o.customer_id\nJOIN order_payments p ON o.order_id = p.order_id\nGROUP BY c.customer_id\nORDER BY total_spent DESC\nLIMIT 100;\n",
        "NameQuery" : "SELECT c.customer_id, SUM(p.payment_value) AS total_spent\nFROM customers c\nJOIN orders o ON c.customer_id = o.customer_id\nJOIN order_payments p ON o.order_id = p.order_id\nGROUP BY c.customer_id\nORDER BY total_spent DESC\nLIMIT 100;\n",
        "IntersectionQuery" : "SELECT c.customer_id, SUM(p.payment_value) AS total_spent\nFROM customers c\nJOIN orders o ON c.customer_id = o.customer_id\nJOIN order_payments p ON o.order_id = p.order_id\nGROUP BY c.customer_id\nORDER BY total_spent DESC\nLIMIT 100;\n",
        "UnionQuery" : "SELECT c.customer_id, SUM(p.payment_value) AS total_spent\nFROM customers c\nJOIN orders o ON c.customer_id = o.customer_id\nJOIN order_payments p ON o.order_id = p.order_id\nGROUP BY c.customer_id\nORDER BY total_spent DESC\nLIMIT 100;\n"
    }
    return jsonify(response)










