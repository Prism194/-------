'''
This Python code incorporates material from the CS50 course, which is 
available under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 
International License. You can find more about this license here: 
https://creativecommons.org/licenses/by-nc-sa/4.0/

For original CS50 materials, visit: https://cs50.harvard.edu/
'''
from flask import redirect, session
from functools import wraps

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