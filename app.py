import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import login_required

app = Flask(__name__)
app.debug = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Just a dictionary, setting the path to the folder where the images will be edited
app.config['UPLOAD_FOLDER'] = './images'

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///info.db")

# Pagination pages
PER_PAGE = 5

@app.route('/')
def home():
  # You can add logic for your homepage here if needed
  # database -> image, product name, price
  return render_template('index.html')  # Assuming you have an index.html

@app.route('/about')
def about():
  # You can pass data to product1.html if needed using variables here
  return render_template('about.html')

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    product_name_error = None
    quantity_error = None
    price_error = None
    image_error = None
    if request.method == "POST":
        product_name = request.form.get("product_name")
        # check if the product name is input
        if not product_name:
            product_name_error = "Please input product name"

        quantity = request.form.get("quantity")
        # check if the quantity is input
        if not quantity:
            quantity_error = "Please input stock"
        # check if the quantity is valid, only takes 0 and positive integer
        if quantity and not quantity.isdigit():
            quantity_error = "Please input appropriate stock"

        price = request.form.get("price")
        # check if the price is input
        if not price:
            price_error = "Please input price"
        # check if the price is valid, only takes 0 and positive integer
        if price and not price.isdigit():
            price_error = "Please input appropriate price"
        
        file = request.files.get("image")
        if file and allowed_file(file.filename):
            # Sanitizes the filename and makes it secure
            filename = secure_filename(file.filename)
            # Assuming you have a function to generate the next product id or similar unique identifier
            new_filename = f"product{get_next_product_id()}.{get_extension(filename)}"
            # Make the file path compatible with operating system
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            file.save(file_path)
        else:
            image_error = "Invalid or no image provided"

        if not any([product_name_error, quantity_error, price_error, image_error]):
            db.execute("INSERT INTO products (productname, quantity, price) VALUES(?, ?, ?)", product_name, quantity, price)
            return redirect("/manage")
        else:
            return render_template("add.html", product_name_error=product_name_error, quantity_error=quantity_error, price_error=price_error, image_error=image_error)        
    else:
        return render_template("add.html")
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'webp', 'gif'}

def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

def get_next_product_id():
    # Logic to get the next product ID or maximum product ID from your database
    result = db.execute("SELECT MAX(id) FROM products")
    max_id = result[0]['MAX(id)']
    return max_id + 1 if max_id else 1

# Just a dictionary, setting the path to the folder where the images will be uploaded
app.config['UPLOAD_FOLDER'] = './images'

@app.route('/manage')
@login_required
def manage():
    # check if the page parameter is in URL, and get it
    page = int(request.args.get('page', 1))
    product_id = db.execute("SELECT id FROM products")
    product_name = db.execute("SELECT productname FROM products")
    quantity = db.execute("SELECT quantity FROM products")
    price = db.execute("SELECT price FROM products")
    length = len(product_id)
    products = []
    for i in range(length):
        products.append({"index": i + 1, "product_name": product_name[i]["productname"], "quantity": quantity[i]["quantity"], "price": price[i]["price"], "product_id":int(product_id[i]["id"])})
    
    # find the start and end index of the products to display
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    products = products[start:end]
    
    pagination_links = []
    total_pages = (length // PER_PAGE) + (length % PER_PAGE > 0)
    for num in range(1, total_pages + 1):
        link = url_for('manage', page=num)  # Generate URL for each page
        pagination_links.append(link)
    return render_template("manage.html", products=products, pagination_links=pagination_links, page=page)

@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit(product_id):
    if request.method == 'POST':
        old_product_name = db.execute("SELECT productname FROM products WHERE id = ? ", product_id)
        old_quantity = db.execute("SELECT quantity FROM products WHERE id = ? ", product_id)
        old_price = db.execute("SELECT price FROM products WHERE id = ? ", product_id)
        product_name_error = None
        quantity_error = None
        price_error = None
        image_error = None
        product_name = request.form.get("product_name")
        # check if the product name is input
        if not product_name:
            product_name_error = "Please input product name"

        quantity = request.form.get("quantity")
        # check if the quantity is input
        if not quantity:
            quantity_error = "Please input stock"
        # check if the quantity is valid, only takes 0 and positive integer
        if quantity and not quantity.isdigit():
            quantity_error = "Please input appropriate stock"

        price = request.form.get("price")
        # check if the price is input
        if not price:
            price_error = "Please input price"
        # check if the price is valid, only takes 0 and positive integer
        if price and not price.isdigit():
            price_error = "Please input appropriate price"
        
        file = request.files.get("image")
        if file and allowed_file(file.filename):
            # Sanitizes the filename and makes it secure
            filename = secure_filename(file.filename)
            
            # Assuming you have a function to generate the next product id or similar unique identifier
            new_filename = f"product{product_id}.{get_extension(filename)}"

            # Make the file path compatible with operating system
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            delete_existing_image(product_id)
            file.save(file_path)
        else:
            image_error = "Invalid or no image provided"
        if not any([product_name_error, quantity_error, price_error, image_error]):
            product_list=[]
            product_list = db.execute("SELECT productname FROM products")
            length = len(product_list)
            for i in range(length):
                product_list[i] = (product_list[i]["productname"])
            index = product_list.index(old_product_name[0]["productname"])
            page = index // PER_PAGE + 1           
            db.execute("UPDATE products SET productname = ?, quantity = ?, price = ? WHERE id = ?", product_name, quantity, price, product_id)
            return redirect(url_for('manage', page=page))
        else:
            return render_template("edit.html", product_id=product_id, old_product_name=old_product_name[0]["productname"], old_quantity=old_quantity[0]["quantity"], old_price=old_price[0]["price"], product_name_error=product_name_error, quantity_error=quantity_error, price_error=price_error, image_error=image_error)        
    # get
    else:
        old_product_name = db.execute("SELECT productname FROM products WHERE id = ? ", product_id)
        old_quantity = db.execute("SELECT quantity FROM products WHERE id = ? ", product_id)
        old_price = db.execute("SELECT price FROM products WHERE id = ? ", product_id)
        return render_template("edit.html", product_id=product_id, old_product_name=old_product_name[0]["productname"], old_quantity=old_quantity[0]["quantity"], old_price=old_price[0]["price"])
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'webp', 'gif'}

def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

def delete_existing_image(product_id):
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.startswith(f"product{product_id}."):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/delete/<int:product_id>')
@login_required
def delete(product_id):
    product_name = db.execute("SELECT productname FROM products WHERE id = ? ", product_id)
    product_list=[]
    product_list = db.execute("SELECT productname FROM products")
    length = len(product_list)
    for i in range(length):
        product_list[i] = (product_list[i]["productname"])
    index = product_list.index(product_name[0]["productname"])
    if index % PER_PAGE == 0:
        page = index // PER_PAGE
    else:
        page = index // PER_PAGE + 1
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.startswith(f"product{product_id}."):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    db.execute("DELETE FROM products WHERE id = ?", product_id)
    return redirect(url_for('manage', page=page))
          

@app.route('/all_products')
def all_products():
  # You can pass data to product1.html if needed using variables here
  
  return render_template('all_products.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    username_error = None
    password_error = None
    confirmation_error = None
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            username_error = "Please input your username"
        check = db.execute("SELECT username FROM users WHERE username == ?", username)
        if check:
            username_error = "Your username is redundant"
        password = request.form.get("password")
        if not password:
            password_error = "Please input your password"
        confirmation = request.form.get("confirmation")
        if not confirmation:
            confirmation_error = "Please input confirmation password"
        if password and confirmation and password != confirmation:
            confirmation_error = "Your password is not identical with confirmation"
        if not any([username_error, password_error, confirmation_error]):
            hash = generate_password_hash(password, method='pbkdf2', salt_length=16)
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)
            return redirect("/login")
        else:
            return render_template("register.html", username_error=username_error, password_error=password_error, confirmation_error=confirmation_error)
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()
    username_error = None
    password_error = None
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            username_error = "Please input your username"

        # Ensure password was submitted
        if not request.form.get("password"):
            password_error = "Please input your password"

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            password_error = "invalid username or password"

        # Remember which user has logged in
        if not any([username_error, password_error]):
            session["user_id"] = rows[0]["id"]
            # Redirect user to home page
            return redirect("/")
        else:
            return render_template("login.html", username_error=username_error, password_error=password_error)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")   

if __name__ == '__main__':
    app.run()