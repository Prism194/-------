# Scrupulous shopping mall

This project is a scrupulous shopping mall homepage, designed to enhance your project's marketing and user experience.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Download and Installation

Download on github
Clone the repo: 
```
git clone https://github.com/Prism194/Scrupulous-shopping-mall.git
```

### Prerequisites

This project requires Python 3 and the packages listed in the `requirements.txt` file. 
To install these packages, navigate to the project directory and run the following command:

bash
pip install -r requirements.txt

You need to create a table in the database as follows.
```sql
CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL);
CREATE UNIQUE INDEX username ON users (username);
CREATE TABLE products (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, productname TEXT NOT NULL, quantity INTEGER NOT NULL, price INTEGER NOT NULL, image_extension TEXT, description TEXT);
CREATE TABLE cart(user_id INTEGER, product_id INTEGER, quantity INTEGER);
```

## Structure
This project constructed a backend using the flask framework.
This project configured the database using the sqlite 3 database provided by cs50.
The main Python application is app.py. This file runs the web server and handles requests.
The HTML files are located in the templates directory. These files define the structure and content of the web pages.
In static folder, it handles static images and css file

## Usage
Key Features:
About Section:
Displays a comprehensive company overview, highlighting your business's mission, values, and offerings.

Product Management:
Admin users can log in (using id: admin, pw: 1234) and access the "Manage Products" section.
Add new products using the "Add" button.
Edit existing products by selecting the product and clicking "Edit."
Delete products using the "Delete" button.

User Registration and Login:
Users can register for an account using the "Register" button.
Passwords are securely hashed and stored, ensuring data protection.
Registered users can log in and access the full functionality of the site.

Shopping Cart and Purchase Simulation:
Users can add products to their cart and proceed to "Purchase."
While not a real transaction system, this feature simulates the purchase process and updates product inventory.

## Specification

1. @app.route(‘/’)
- The product information stored in the products is stored in the list in the form of a dictionary and displayed in the latest order.

2. @app.route(‘/about’)
- Displays the introduction page.
- I put in the ability to auto-scroll by pressing the table of contents through the Javascript syntax in html.

3. @app.route('/all_products')
- The product information stored in the products is stored in the list in the form of a dictionary and displayed in the latest order.
- Use the PageNation function.

4. @app.route('/product/<int:product_id>')
- Receive product_id to display detailed pages for a particular product.

5. @app.route('/manage')
- The product information stored in the products database is stored in the list in the form of a dictionary and displayed in the latest order.
- Use the PageNation function.

6. @app.route('/add', methods=['GET', 'POST'])
- GET : Displays the add.html file.
- POST
    - Receive product name, description, quantity, price, and image information from the manager.
    - The product name and explanation go through the process of checking whether the content exists.
    - The quantity and price go through the process of checking whether the content exists and whether it is an integer greater than or equal to zero.
    - > The reason why 0 can be entered is because it takes into account the case where the quantity and price cannot be determined when the product is received.
    - The image goes through the process of verifying that the content exists and that the appropriate extension has been entered.
    - When an image is stored in a database, the image name is not directly stored in the database. The image name was combined with the product ID and stored on the server, and only the extension was stored in the database separately.
    - > When adding a new product to the products database, a new file name is created by assigning a higher ID from the existing ID, which causes problems if the entire new file name is created in the database. When modifying a picture in the edit function, the existing product ID remains the same, but if the extension changes, saving the entire file name creates a problem that requires cutting and calculating the name again in the backend code. Therefore, it is necessary to manage the product id and the extension separately to modify the picture more efficiently.
    - When inserting an image, the try-except phrase, the database's commitment, and rollback logic were used to ensure that the database ID was not wasted.
    - First, if there are no errors in product name, description, quantity, and price, first, the ID is temporarily assigned to the database
    - After that, if the image file is valid, commit it to the database to confirm the ID
    - If the image file is not valid, rollback and return the temporarily assigned ID
    - > Prevent garbage id and values from occurring in the database when an unexpected error occurs when inserting an image.

7. @app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
- GET : Get the existing product name, description, quantity, and price and display it on the edit console.
    - This is for your convenience, and by displaying the specifications of the pre-edit product in the Edit console, you don't have to remember the previous values.
- POST
    - You can modify product name, description, quantity, price, and image. Logic is the same as add function.
    - Unlike add, it made it possible to modify the data without necessarily entering the image.
    - > At this time, the image will remain the same as the image stored on the server.
    - If the modification is successful, we have used the PageNation function to allow you to go directly to the page where the product is located in the manage console.
    - If the correction fails, receive the existing product name, description, quantity, and price, display it on the edit console, and show the error.
    - If the quality is 0, clear the product information from the cart database of all consumers.

8. @app.route('/delete/<int:product_id>')
- Delete the desired product based on the product id
- After deletion, we used the PageNation feature to allow you to go directly to the page where the product is located in the manage console.
- When you delete a product, it clears its product information from the cart database of all consumers.

9. @app.route("/register", methods=["GET", "POST"])
- Get the user's username, password, confirmation and store it in the user database.
- Verify that the contents exist for username, password, and confirmation.
- Verify that the password and confirmation values are the same.
- If there are no errors, use the hashing function in the werkzeug library to hashen the password and save it.

10. @app.route("/login", methods=["GET", "POST"])
- Get the user's username, password, confirmation, and enter the user's unique id value in the session when the login is successful compared to the database.
- Both username and password verify that the contents exist and that they match the database. 

11. @app.route("/logout")
- Delete the value stored in the session and return it to the main home page.

12. @app.route("/add_to_cart/<int:product_id>", methods=["POST"])
- It receives products and quantities to purchase from users and stores them in the cart database.
- It goes through the process of checking whether the quantity exists and whether it is an integer greater than or equal to zero.
- Make sure the quantity is higher than the inventory.
- When you put it in a cart, if it already exists in the cart, increase the quantity of that product only, and if it doesn't exist, put a new product in the database. 

13. @app.route("/cart")
- Identify the user's id through session and extract all product information that the user has from the cart database.
- Import information such as product name and price from the product database through product_id contained in cart 
-> We saved memory by reducing the amount of space that overlaps between databases as much as possible.
- If the quantity contained by the user becomes larger than the inventory, the quantity of goods contained in the cart must not exceed the quantity in stock.
-> This situation does not normally occur under code 12, but if the company suddenly reduces its inventory, the amount in the user cart may be larger than the company's inventory, so we have created an additional code.
- Use the paganization function to show the user what is contained in the cart. 

14. @app.route("/update_quantity/<int:product_id>", methods=["POST"])
- It contains the ability to update the quantity contained in the cart.
- Verify that the quantity is entered and that the quantity is an integer greater than or equal to zero.
- Make sure the quantity is higher than the inventory.

15. @app.route("/delete_item/<int:product_id>")
- It contains the ability to delete the product contained in the cart. 

16. @app.route('/purchase', methods=['POST'])
- It contains the ability to purchase products contained in the cart.
- It is not actually purchased, but when the user presses the purchase button, the inventory is reduced by the quantity purchased.
- The product cannot be purchased in an empty cart, and an error message was displayed.
- The try-except syntax allows the database to be recovered in the event of an unexpected error. 

17. loading.js
- When using functions such as membership registration, login, and purchase, loading was made to appear until the data was fully entered/updated and redirected in the database.
- It is a function based on the inconvenience of the actual user, and if the Internet or server is slow, an error occurs after multiple clicks, so loading is shown to the user during the processing time.


## Authors
Na Seongchan - Initial work

## Acknowledgments

* This project uses code from [startbootstrap-shop-homepage](https://github.com/StartBootstrap/startbootstrap-shop-homepage). The original code is licensed under the MIT license.
* This project uses code from [startbootstrap-shop-item](https://github.com/StartBootstrap/startbootstrap-shop-item). The original code is licensed under the MIT license.

* This project also uses code from the CS50 course. The original code is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) license](https://cs50.harvard.edu/x/2024/license/).

## License
This project is licensed a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) license. - see the [LICENSE.txt](LICENSE.txt) file for details. Please note that this license does not apply to the code from[startbootstrap-shop-homepage](https://github.com/StartBootstrap/startbootstrap-shop-homepage), [startbootstrap-shop-item](https://github.com/StartBootstrap/startbootstrap-shop-item) and the CS50 course, which have their own licenses.
