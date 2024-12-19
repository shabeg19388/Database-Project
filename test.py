from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
import os

load_dotenv()

app = Flask(__name__)
CORS(app, origins = 'http://localhost:3000')
GPTClient = OpenAI(api_key = os.environ['OPEN_API_KEY'])
GeminiClient = OpenAI(api_key = os.environ['GEMINI_API_KEY'], base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

def getGPTcompletion(query : str)  -> str:
    #have to fix schema and add examples
    completion = GPTClient.chat.completions.create(model = 'gpt-4o-mini',
        messages = [
            {
                'role' : 'system',
                'content' : """Give the SQL query needed to resolve a user input. There is no need for explanation or anything just return the query compatible with mySQL. 
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
                """
            },
            {
            'role' : 'user',
            'content' : query
            }])
    return (completion.choices[0].message.content).replace('sql\n', '').replace('```','')

def getGeminiCompletion(query : str, columns : str)  -> str:
    completion = GeminiClient.chat.completions.create(model = 'gemini-1.5-flash',
        messages = [
            {
                'role' : 'system',
                'content' : """Give the SQL query needed to resolve a user input. There is no need for explanation or anything just return the query compatible with mySQL. 
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
                """
            },
            {
            'role' : 'user',
            'content' : f'{query} with columns names {columns}'
            }])
    return (completion.choices[0].message.content).replace('sql\n', '').replace('```', '')


@app.post('/query')
def query():
    GPTQuery = getGPTcompletion(request.json['query'])

    #After querying the data we want to extract the column names and send it to the gemini query. Thinking about bias: We need to make sure that the prompt we are giving Gemini isn't too biased. My solution: We try all approaches have gemini come up with its own query, give the column names from gpt to gemini, give only the number of columns from gemini. For the intersection and union we can just use the query where we give the column names.
    
    GeminiQuery = getGeminiCompletion(request.json['query'])
    
    UnionQuery = f'({GPTQuery}) UNION ({GeminiQuery}))'
    IntersectionQuery = f'({GPTQuery}) INTERSECTION ({GeminiQuery})'
    return jsonify({'GPTQuery': GPTQuery, 'GeminiQuery': GeminiQuery})


@app.post('/test')
def test():
    print(request.json)
    gpt = [
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
    ]
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
    ]
    response = {
        'gpt' : gpt,
        'gemini' : gemini,
        'union' : union,
        'intersection' : intersection,
        'gemini_name' : gemini_name,
        'gemini_num' : gemini_num,
        "GPTQuery" :  "SELECT c.customer_id, SUM(p.payment_value) AS total_spent\nFROM customers c\nJOIN orders o ON c.customer_id = o.customer_id\nJOIN order_payments p ON o.order_id = p.order_id\nGROUP BY c.customer_id\nORDER BY total_spent DESC\nLIMIT 100;\n",
        "GeminiQuery" : "SELECT\n  c.customer_unique_id\nFROM customers AS c\nJOIN orders AS o\n  ON c.customer_id = o.customer_id\nJOIN order_payments AS op\n  ON o.order_id = op.order_id\nGROUP BY\n  c.customer_unique_id\nORDER BY\n  SUM(op.payment_value) DESC\nLIMIT 100;\n\n",
        "GeminiNumQuery" : "SELECT c.customer_id, SUM(p.payment_value) AS total_spent\nFROM customers c\nJOIN orders o ON c.customer_id = o.customer_id\nJOIN order_payments p ON o.order_id = p.order_id\nGROUP BY c.customer_id\nORDER BY total_spent DESC\nLIMIT 100;\n",
        "GeminiNameQuery" : "SELECT c.customer_id, SUM(p.payment_value) AS total_spent\nFROM customers c\nJOIN orders o ON c.customer_id = o.customer_id\nJOIN order_payments p ON o.order_id = p.order_id\nGROUP BY c.customer_id\nORDER BY total_spent DESC\nLIMIT 100;\n",
        "IntersectionQuery" : "SELECT c.customer_id, SUM(p.payment_value) AS total_spent\nFROM customers c\nJOIN orders o ON c.customer_id = o.customer_id\nJOIN order_payments p ON o.order_id = p.order_id\nGROUP BY c.customer_id\nORDER BY total_spent DESC\nLIMIT 100;\n",
        "UnionQuery" : "SELECT c.customer_id, SUM(p.payment_value) AS total_spent\nFROM customers c\nJOIN orders o ON c.customer_id = o.customer_id\nJOIN order_payments p ON o.order_id = p.order_id\nGROUP BY c.customer_id\nORDER BY total_spent DESC\nLIMIT 100;\n"
    }
    return jsonify(response)










