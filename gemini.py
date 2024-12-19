import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

GeminiClient = OpenAI(api_key = os.environ['GEMINI_API_KEY'], base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
GPTClient = OpenAI(api_key = os.environ['OPEN_API_KEY'])
def getGeminicompletion(query : str)  -> str:
    completion = (GeminiClient.chat.completions.create(model = 'gemini-1.5-flash',
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
                Convert the user input into a valid SQL query and return an executable query for the given database without any explanation. 

                Return the resulting query in compact SQL.
                """
            },
            {
            'role' : 'user',
            'content' : query
            }]).choices[0].message.content).replace('sql\n', '').replace('```','')
    return completion

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

print(getGPTcompletion('Find the most popular product in March'))