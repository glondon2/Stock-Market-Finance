import csv
import requests
import json

from flask import redirect, render_template, request, session, url_for
from functools import wraps

def apology(top="", bottom=""):
    """Renders message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
            ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=escape(top), bottom=escape(bottom))

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def lookup(symbol):
    key = '01O7OYJKAUNK9TQ7'
    url = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={}&apikey={}".format(symbol, key)
    if symbol.startswith('^'):
        return None
    if ',' in symbol:
        return None
    page = requests.get(url)
    json = page.json()
    if len(json['Global Quote']) < 1:
        return "Something went wrong"
    else:
        return {
            "name": json['Global Quote']['01. symbol'],
            "price": json['Global Quote']['05. price'],
            "symbol": json['Global Quote']['01. symbol']
        }
def usd(value):
    """Formats value as USD."""
    return "${:,.2f}".format(value)
