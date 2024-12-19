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


#have to fix schema and add examples also can add an example row from each table. Also fix schema in frontend.
sys_message = """Give the SQL query needed to resolve a user input. There is no need for explanation or anything just return the query compatible with mySQL. 
                The database is a Brazilian e-commerce database from O-List (in English). Only return the SQL query given the user input.
                The schema for the database is:
                    "customers(customer_id [PK], customer_unique_id, zip_code [FK: geolocation.zip_code], city, state): Has customer id and address information. 

                    orders(order_id [PK], customer_id [FK: customers.customer_id], order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date): Has order information including customer, status of order, purchase time, approval time, delivery to carrier, delivery to customer, and estimated delivery date to customer.

                    order_payments(order_id [FK: orders.order_id], payment_sequential, payment_type, payment_installments, payment_value): Has payment information for each order including installments and multiple payment methods (payment_sequential).

                    order_reviews(review_id [PK], order_id [FK: orders.order_id], review_score, review_comment_title, review_comment_message, review_creation_date, review_answer_timestamp): Has reviews for each order including score, title, message, date and answer from seller timestamp.

                    geolocation(zip_code [PK], lat, lang, city, state): Has location information for each zip code.

                    product_category_name_ translation(category_name [PK], category_name_english): Has translation for category from portugese to english.

                    products(product_id [PK], category_name [FK: product_category_name_translation.category_name], name_length, description_length, photo_qty, weight_g, length_cm, height_cm, width_cm): Has product information including category in portugese, product name length, product description length, number of photos, weight of item and dimensions of item.

                    sellers(seller_id [PK], zip_code [FK: geolocation.zip_code], city, state): Has inforation on seller including address information.

                    order_items(order_id [FK: orders.order_id], order_item_id [PK], product_id [FK: products.product_id], 
                    seller_id [FK: sellers.seller_id], shipping_limit_date, price, freight_value): Has item information for each order including item number, product id, seller id, limit date for seller to hand over item to carrier, item price and item freight value item (if an order has more than one item the freight value is splitted between items)."   


                If you think that the user input is outside the scope of this schema then throw an error out of scope. 
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
    completion_num = GeminiClient.chat.completions.create(model = 'gemini-1.5-flash',
        messages = [
            {
                'role' : 'system',
                'content' : sys_message
            },
            {
            'role' : 'user',
            'content' : f'{query} with column output {columns}'
            }])
    
    completion_name = GeminiClient.chat.completions.create(model = 'gemini-1.5-flash',
        messages = [
            {
                'role' : 'system',
                'content' : sys_message
            },
            {
            'role' : 'user',
            'content' : f'{query} with {len(columns)} columns'
            }])
    
    GeminiQuery, NumQuery, NameQuery = (completion_base.choices[0].message.content).replace('sql\n', '').replace('```',''), (completion_num.choices[0].message.content).replace('sql\n', '').replace('```',''), (completion_name.choices[0].message.content).replace('sql\n', '').replace('```','')
    return GeminiQuery, NumQuery, NameQuery


@app.post('/query')
def query():
    GPTQuery = getGPTCompletion(request.json['query'])

    #After querying the data we want to extract the column names and send it to the gemini query. Thinking about bias: We need to make sure that the prompt we are giving Gemini isn't too biased. My solution: We try all approaches have gemini come up with its own query, give the column names from gpt to gemini, give only the number of columns from gemini. For the intersection and union we can just use the query where we give the column names.
    
    GeminiQuery, NumQuery, NameQuery = getGeminiCompletion(request.json['query'])
    
    UnionQuery = f'({GPTQuery}) UNION ({NameQuery}))'
    IntersectionQuery = f'({GPTQuery}) INTERSECTION ({GeminiQuery})'
    return jsonify({'GPTQuery': GPTQuery, 'GeminiQuery': GeminiQuery})


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










