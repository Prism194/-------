'''
This Python code incorporates material from the CS50 course, which is 
available under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 
International License. You can find more about this license here: 
https://creativecommons.org/licenses/by-nc-sa/4.0/

For original CS50 materials, visit: https://cs50.harvard.edu/
'''
import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import *

app = Flask(__name__)
app.debug = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Just a dictionary, setting the path to the folder where the images will be edited
app.config['UPLOAD_FOLDER'] = './static/product_images'

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///info.db")

# Pagination pages

# common pages
PER_PAGE = 7

# manage pages
PER_PAGE_MANAGE = 5

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'webp', 'gif'}

def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

def delete_existing_image(product_id):
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.startswith(f"product{product_id}."):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/')
def home():
    # database -> image, product name, price    
    data, length = get_page_data(0, PER_PAGE)
    products = []
    for i in range(length):
        products.append({"product_name": data[i]["productname"], "quantity": data[i]["quantity"], "price": data[i]["price"], "product_id":int(data[i]["id"]), "image_extension": data[i]["image_extension"]})

    return render_template('index.html', products = products)

@app.route('/about')
def about():
  
  return render_template('about.html')

@app.route('/all_products')
def all_products():
    all_product_length = len(db.execute("SELECT * FROM products"))
    # database -> image, product name, price, etc
    page = int(request.args.get('page', 1))
    start = (page - 1) * PER_PAGE
    data, length = get_page_data(start, PER_PAGE)
    
    products = []
    for i in range(length):
        products.append({"product_name": data[i]["productname"], "quantity": data[i]["quantity"], "price": data[i]["price"], "product_id":int(data[i]["id"]), "image_extension": data[i]["image_extension"]})

    pagination_links = make_pagination_link(all_product_length, PER_PAGE, 'all_products')    
        
    return render_template('all_products.html', products = products, pagination_links=pagination_links, page=page)

@app.route('/product/<int:product_id>')
def product(product_id):
    data = db.execute("SELECT * FROM products WHERE id = ?", product_id)
    return render_template('product.html', product_id=product_id, product_name=data[0]["productname"], quantity=data[0]["quantity"], price=data[0]["price"], image_extension=data[0]["image_extension"], description=data[0]["description"])

# Search by get method    
@app.route('/search')
def search():
    search = request.args.get('search', '')
    if not search:
        return redirect('/')
    search = search.lower()
    page = int(request.args.get('page', 1))
    data = db.execute("SELECT * FROM products WHERE productname LIKE ? ORDER BY id desc", f"%{search}%")
    length = len(data)
    products = []
    for i in range(length):       
        products.append({"product_name": data[i]["productname"], "quantity": data[i]["quantity"], "price": data[i]["price"], "product_id":int(data[i]["id"]), "image_extension": data[i]["image_extension"]})
    
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    products = products[start:end]
    
    pagination_links = []
    total_pages = (length // PER_PAGE) + (length % PER_PAGE > 0)
    for num in range(1, total_pages + 1):
        link = url_for('search', search=search, page=num)  # Generate URL for each page
        pagination_links.append(link)
    
    return render_template('search.html', search = search, products = products, pagination_links=pagination_links, page=page)

# autocomplete function, using Ajax
@app.route('/autocomplete')
def autocomplete():
    search = request.args.get('search', '')
    if not search:
        return jsonify([])

    search = search.lower()
    data = db.execute("SELECT productname FROM products WHERE productname LIKE ? ORDER BY id desc", f"%{search}%")
    suggestions = [item['productname'] for item in data]
    return jsonify(suggestions)

@app.route('/manage')
@login_required
def manage():
    # check if the page parameter is in URL, and get it
    all_product_length = len(db.execute("SELECT * FROM products"))
    page = int(request.args.get('page', 1))
    start = (page - 1) * PER_PAGE_MANAGE
    data, length = get_page_data(start, PER_PAGE_MANAGE)
   
    products = []
    for i in range(length):
        products.append({"index": i + 1 + start, "product_name": data[i]["productname"], "quantity": data[i]["quantity"], "price": data[i]["price"], "product_id":int(data[i]["id"])})
        
    pagination_links = make_pagination_link(all_product_length, PER_PAGE_MANAGE, 'manage')
    return render_template("manage.html", products=products, pagination_links=pagination_links, page=page)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    
    if request.method == "POST":
        image_error = None

        # check the text input error
        product_name = request.form.get("product_name")
        description = request.form.get("description")
        quantity = request.form.get("quantity")
        price = request.form.get("price")
        product_name_error, description_error, quantity_error, price_error = error_message(product_name, description, quantity, price)
        
        if any([product_name_error, quantity_error, price_error, description_error]):
            flash(product_name_error, 'product_name_error')  # Flash error with category
            flash(description_error, 'description_error')
            flash(quantity_error, 'quantity_error')
            flash(price_error, 'price_error')
            return redirect('/add')
        
        # get image file
        file = request.files.get("image")            
        # Begin a transaction
        db.execute("BEGIN")
        db.execute("INSERT INTO products (productname, quantity, price, description) VALUES(?, ?, ?, ?)", product_name, quantity, price, description)
        result = db.execute("SELECT MAX(id) FROM products")
        max_id = result[0]['MAX(id)']  # Adjusted for accessing id

        if file and allowed_file(file.filename):
            try:
                # saves the file when the image is given, and the file is valid
                filename = secure_filename(file.filename)
                new_filename = f"product{max_id}.{get_extension(filename)}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                file.save(file_path)

                db.execute("UPDATE products SET image_extension = ? WHERE id = ?", get_extension(filename), max_id)
                db.execute("COMMIT")
                return redirect("/manage")
            except Exception as e:
                db.execute("ROLLBACK")
                image_error = str(e)
                flash(image_error, 'image_error')
                return redirect('/add')
        else:
            # if the image is not given, or the image is invalid
            db.execute("ROLLBACK")
            image_error = "Invalid or no image provided"
            flash(image_error, 'image_error')
            return redirect('/add')
    else:
        return render_template("add.html")

@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit(product_id):
    data = db.execute("SELECT * FROM products WHERE id = ? ", product_id)
    old_product_name = data[0]["productname"]
    old_quantity = data[0]["quantity"]
    old_price = data[0]["price"]
    old_description = data[0]["description"]
    if request.method == 'POST':
        product_name = request.form.get("product_name")
        description = request.form.get("description")
        quantity = request.form.get("quantity")
        price = request.form.get("price")
        image_error = None
        product_name_error, description_error, quantity_error, price_error = error_message(product_name, description, quantity, price)

        # check if the text input is valid
        if any([product_name_error, quantity_error, price_error, description_error]):
            return render_template("edit.html", product_id=product_id, old_product_name = old_product_name, old_quantity = old_quantity, old_price = old_price, old_description=old_description, product_name_error=product_name_error, quantity_error=quantity_error, price_error=price_error, image_error=image_error)

        file = request.files.get("image")
        # if the image is given, and the image is valid, it replaces the existing image
        if file and allowed_file(file.filename):
            # Sanitizes the filename and makes it secure
            filename = secure_filename(file.filename)
            new_filename = f"product{product_id}.{get_extension(filename)}"

            # Make the file path compatible with operating system
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            delete_existing_image(product_id)
            file.save(file_path)

            # Update the product information in the database
            product_list = db.execute("SELECT id FROM products")
            product_list.reverse()
            length = len(product_list)
            for i in range(length):
                if product_list[i]["id"] == product_id:
                    index = i
                    break
            page = index // PER_PAGE_MANAGE + 1           
            db.execute("UPDATE products SET productname = ?, quantity = ?, price = ?, description = ?, image_extension = ? WHERE id = ?", product_name, quantity, price, description, filename.rsplit('.', 1)[1].lower(), product_id)
            if int(quantity) == 0:
                db.execute("DELETE FROM cart WHERE product_id = ?", product_id)
            return redirect(url_for('manage', page=page))
        
        # if the image is not given, but the text input is valid, it updates the product information
        elif not file:           
            product_list = db.execute("SELECT id FROM products")
            product_list.reverse()
            length = len(product_list)
            for i in range(length):            
                if product_list[i]["id"] == product_id:
                    index = i
                    break
            page = index // PER_PAGE_MANAGE + 1           
            db.execute("UPDATE products SET productname = ?, quantity = ?, price = ?, description = ? WHERE id = ?", product_name, quantity, price, description, product_id)
            if int(quantity) == 0:
                db.execute("DELETE FROM cart WHERE product_id = ?", product_id)
            return redirect(url_for('manage', page=page))
        
        # if the image is given, but the image is invalid, it returns an error message
        else:
            image_error = "Invalid image format"
            return render_template("edit.html", product_id=product_id, old_product_name = old_product_name, old_quantity = old_quantity, old_price = old_price, old_description=old_description, product_name_error=product_name_error, quantity_error=quantity_error, price_error=price_error, image_error=image_error)

    # get
    else:
        return render_template("edit.html", product_id=product_id, old_product_name = old_product_name, old_quantity = old_quantity, old_price = old_price, old_description=old_description)


@app.route('/delete/<int:product_id>')
@login_required
def delete(product_id):
    
    product_list = db.execute("SELECT id FROM products")
    product_list.reverse()
    length = len(product_list)
    for i in range(length):
        if product_list[i]["id"] == product_id:
            index = i + 1
            break

    if index % PER_PAGE_MANAGE == 0:
        page = index // PER_PAGE_MANAGE
    else:
        page = index // PER_PAGE_MANAGE + 1
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.startswith(f"product{product_id}."):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    db.execute("DELETE FROM products WHERE id = ?", product_id)
    db.execute("DELETE FROM cart WHERE product_id = ?", product_id)
    return redirect(url_for('manage', page=page))

@app.route("/register", methods=["GET", "POST"])
def register():
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
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")   

@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    
    quantity_error = None
    # check if the quantity is input
    quantity = request.form.get("quantity")
    if not quantity:
        quantity_error = "Please input stock"
    # check if the quantity is valid, only takes 0 and positive integer
    if quantity and not quantity.isdigit():
        quantity_error = "Please input appropriate stock"
    stock = db.execute("SELECT quantity FROM products WHERE id = ?", product_id)
    if int(quantity) > int(stock[0]["quantity"]):
        quantity_error = "Not enough stock"
    if quantity_error:
        return render_template("error.html", quantity_error=quantity_error)
    check = db.execute("SELECT user_id FROM cart WHERE user_id = ? AND product_id = ?", session["user_id"], product_id)
    if check:
        db.execute("UPDATE cart SET quantity = quantity + ? WHERE user_id = ? AND product_id = ?", quantity, session["user_id"], product_id)
    else:
        db.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES(?, ?, ?)", session["user_id"], product_id, quantity)

    return redirect("/cart")

@app.route("/cart")
@login_required
def cart():
    cart = db.execute("SELECT * FROM cart WHERE user_id = ?", session["user_id"])
    products = []
    cnt = 0
    total = 0
    
    product_list = db.execute("SELECT * FROM products")
    for item in cart:
        product_id = item["product_id"]
        for product in product_list:
            if product["id"] == product_id:
                product_name = product["productname"]
                quantity = item["quantity"]
                if int(quantity) > int(product["quantity"]):
                    quantity = product["quantity"]
                    db.execute("UPDATE cart SET quantity = ? WHERE product_id = ? AND user_id = ?", quantity, product_id, session["user_id"])
                price = product["price"]
                products.append({"index" : cnt + 1, "product_id": product_id, "product_name": product_name, "quantity": quantity, "price": price})
                total += int(quantity) * int(price)
                cnt += 1
                break
    
    # check if the page parameter is in URL, and get it
    page = int(request.args.get('page', 1))
    length = len(products)
            
    # find the start and end index of the products to display
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    products = products[start:end]

    pagination_links = []
    total_pages = (length // PER_PAGE) + (length % PER_PAGE > 0)
    for num in range(1, total_pages + 1):
        link = url_for('cart', page=num)  # Generate URL for each page
        pagination_links.append(link)

    return render_template("cart.html", products=products, pagination_links=pagination_links, page=page, total=total)

@app.route("/update_quantity/<int:product_id>", methods=["POST"])
@login_required
def update_quantity(product_id):
    # check if the quantity is input
    new_quantity = request.form.get("quantity")
    if not new_quantity:
        flash('Please input quantity', 'error')
        return redirect('/cart')
    # check if the quantity is valid, only takes 0 and positive integer
    if new_quantity and not new_quantity.isdigit():
        flash('Please input appropriate quantity', 'error')
        return redirect('/cart')
    stock = db.execute("SELECT quantity FROM products WHERE id = ?", product_id)
    if int(new_quantity) > int(stock[0]["quantity"]):
        flash('Not enough stock', 'error')
        return redirect('/cart')

    db.execute("UPDATE cart SET quantity = ? WHERE product_id = ? AND user_id = ?", new_quantity, product_id, session["user_id"])
    return redirect("/cart")
    
@app.route("/delete_item/<int:product_id>")
@login_required
def delete_item(product_id):
    db.execute("DELETE FROM cart WHERE product_id = ? AND user_id = ?", product_id, session["user_id"])
    return redirect("/cart")

@app.route('/purchase', methods=['POST'])
@login_required
def purchase():
    # Start transaction
    db.execute("BEGIN")
    try:
        # Fetch all items in the user's cart
        cart_items = db.execute("SELECT product_id, quantity FROM cart WHERE user_id = ?", session["user_id"])
        if cart_items == []:
            flash('Your cart is empty. Please add items to proceed with purchase.', 'error')
            return redirect('/cart')
        
        # Update the stock quantities in the products table
        for item in cart_items:
            db.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", int(item['quantity']), item['product_id'])
        
        # Clear the user's cart
        db.execute("DELETE FROM cart WHERE user_id = ?", session["user_id"])
        
        # Commit changes if all updates are successful
        db.execute("COMMIT")
    
        return redirect('/')
    except Exception as e:
        db.execute("ROLLBACK")
        return redirect('/cart')

if __name__ == '__main__':
    app.run()