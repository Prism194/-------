'''
This Python code incorporates material from the CS50 course, which is 
available under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 
International License. You can find more about this license here: 
https://creativecommons.org/licenses/by-nc-sa/4.0/

For original CS50 materials, visit: https://cs50.harvard.edu/
'''
from cs50 import SQL
from flask import redirect, session, url_for
from functools import wraps

db = SQL("sqlite:///info.db")

# Decorator to require login
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

# get the product data from the database by descending order
def get_page_data(start, per_page_number):
    data = db.execute("SELECT * FROM products ORDER BY id desc LIMIT ? OFFSET ?", per_page_number, start)
    length = len(data)
    return data, length

def make_pagination_link(length, per_page_number, query_string):
    pagination_links = []
    total_pages = (length // per_page_number) + (length % per_page_number > 0)
    for num in range(1, total_pages + 1):
        link = url_for(f'{query_string}', page=num)  # Generate URL for each page
        pagination_links.append(link)
    return pagination_links

def error_message(product_name, description, quantity, price):
    product_name_error = None
    description_error = None
    quantity_error = None
    price_error = None
    
    # check if the product name is input
    if not product_name:
        product_name_error = "Please input product name"
    
    # check if the description is input
    if not description:
        description_error = "Please input description"

    # check if the quantity is input
    if not quantity:
        quantity_error = "Please input stock"
    # check if the quantity is valid, only takes 0 and positive integer
    if quantity and not quantity.isdigit():
        quantity_error = "Please input appropriate stock"

    # check if the price is input
    if not price:
        price_error = "Please input price"
    # check if the price is valid, only takes 0 and positive integer
    if price and not price.isdigit():
        price_error = "Please input appropriate price"
    return product_name_error, description_error, quantity_error, price_error

