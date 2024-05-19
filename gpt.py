from flask import Flask, request, render_template, redirect, url_for
from cs50 import SQL
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
db = SQL("sqlite:///yourdatabase.db")
app.config['UPLOAD_FOLDER'] = '/path/to/your/upload/directory'

def validate_input(data):
    errors = {}
    if not data.get('product_name'):
        errors['product_name_error'] = "Please input product name"
    if not data.get('description'):
        errors['description_error'] = "Please input description"
    if not data.get('quantity'):
        errors['quantity_error'] = "Please input stock"
    elif not data['quantity'].isdigit():
        errors['quantity_error'] = "Please input appropriate stock"
    if not data.get('price'):
        errors['price_error'] = "Please input price"
    elif not data['price'].isdigit():
        errors['price_error'] = "Please input appropriate price"
    return errors

def insert_product(data):
    db.execute("INSERT INTO products (productname, quantity, price, description) VALUES(?, ?, ?, ?)",
               data['product_name'], data['quantity'], data['price'], data['description'])
    result = db.execute("SELECT MAX(id) FROM products")
    return result[0]['MAX(id)']

def save_image(file, product_id):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        new_filename = f"product{product_id}.{get_extension(filename)}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(file_path)
        db.execute("UPDATE products SET image_extension = ? WHERE id = ?", get_extension(filename), product_id)
        return None
    else:
        return "Invalid or no image provided"

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()
