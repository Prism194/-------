# Scrupulous shopping mall

This project is a scrupulous shopping mall homepage, designed to enhance your project's marketing and user experience.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

This project requires Python 3 and the packages listed in the `requirements.txt` file. 

To install these packages, navigate to the project directory and run the following command:

bash
pip install -r requirements.txt

## Structure
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

## Authors
Na Seongchan - Initial work

## Acknowledgments

* This project uses code from [startbootstrap-shop-homepage](https://github.com/StartBootstrap/startbootstrap-shop-homepage). The original code is licensed under the MIT license.
* This project uses code from [startbootstrap-shop-item](https://github.com/StartBootstrap/startbootstrap-shop-item). The original code is licensed under the MIT license.

* This project also uses code from the CS50 course. The original code is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) license](https://cs50.harvard.edu/x/2024/license/).

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details. Please note that this license does not apply to the code from[startbootstrap-shop-homepage](https://github.com/StartBootstrap/startbootstrap-shop-homepage), [startbootstrap-shop-item](https://github.com/StartBootstrap/startbootstrap-shop-item) and the CS50 course, which have their own licenses.