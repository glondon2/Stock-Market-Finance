#   application.py
#   Aamel Unia
#   application.py
#   aameluni@buffalo.edu
#   This is my implementation of a web application that simulates stock market functionality by allowing 
#   to obtain quotes on stocks and simulate buying and selling stocks by being given an inital capital of $10,000 (CS50 PSET 7).

from SQL import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL('sqlite:///finance.db')


@app.route("/")
@login_required
def index():
    symbol=list()
    share=list()
    price=list()
    total=list()
    # total=[]
    sy = db.execute("SELECT symbol FROM portfolio WHERE id = :id", id= session['user_id'])
    sh = db.execute("SELECT shares FROM portfolio WHERE id = :id", id= session['user_id'])
    pr = db.execute("SELECT price FROM portfolio WHERE id = :id", id= session['user_id'])
    for i in range (len(sy)):
        symbol.append(sy[i]["symbol"].upper())
    for i in range (len(sh)):
        share.append(str(sh[i]["shares"]))  
    for i in range (len(pr)):
        price.append(pr[i]["price"])
    # templates=dict(symbols=symbol,shares=share,prices=price)
    for i in range(len(symbol)):
        total.append(float(price[i])*float(share[i]))
    data = zip(symbol,share,price,total)
    sum = 0.0
    for i in range(len(total)):
        sum+=total[i]
    for i in range(len(total)):
        total[i]=usd(total[i])
    rows = db.execute("SELECT cash FROM users WHERE id=:id", id= session['user_id'])
    sum+=rows[0]["cash"]
    return render_template("index.html", data=data, sum=usd(sum), cash=usd(rows[0]["cash"]))
    
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""
    if request.method == "POST":
        stock = lookup(request.form.get("symbol"));
        if stock is None:
            return apology("invalid stock")
        amount = request.form.get("shares");
        if not amount.isdigit() or (int(amount))%1!=0 or (int(amount))<=0:
            return apology("invalid shares")
        rows = db.execute("SELECT cash FROM users WHERE id=:id", id= session['user_id'])
        if rows[0]["cash"] > float(amount)*float(stock["price"]):
            unique = db.execute("INSERT INTO portfolio (id, symbol, shares, price) VALUES(:id, :symbol, :shares, :price)", id= session['user_id'], symbol=request.form.get("symbol"), shares=request.form.get("shares"), price=stock["price"])
            db.execute("INSERT INTO history (id, symbol, shares, price) VALUES(:id, :symbol, :shares, :price)", id= session['user_id'], symbol=request.form.get("symbol"), shares=request.form.get("shares"), price=stock["price"])
            if not unique:
                temp = db.execute("SELECT shares FROM portfolio WHERE id=:id AND symbol=:symbol", id= session['user_id'], symbol=request.form.get("symbol"))
                db.execute("UPDATE 'portfolio' SET shares=:shares WHERE id=:id AND symbol=:symbol", shares=temp[0]["shares"]+int(request.form.get("shares")), id=session['user_id'], symbol=request.form.get("symbol"))
            db.execute("UPDATE 'users' SET cash=:cash WHERE id=:id", cash=(rows[0]["cash"])-(float(amount)*float(stock["price"])), id= session['user_id']) 
        else:
            return apology("Too little $")
        return redirect(url_for("index"))
        
    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    symbol=list()
    share=list()
    price=list()
    transacted=list()
    # total=[]
    sy = db.execute("SELECT symbol FROM history WHERE id = :id", id= session['user_id'])
    sh = db.execute("SELECT shares FROM history WHERE id = :id", id= session['user_id'])
    pr = db.execute("SELECT price FROM history WHERE id = :id", id= session['user_id'])
    tr = db.execute("SELECT transacted FROM history WHERE id = :id", id= session['user_id'])
    for i in range (len(sy)):
        symbol.append(sy[i]["symbol"].upper())
    for i in range (len(sh)):
        share.append(sh[i]["shares"])  
    for i in range (len(pr)):
        price.append(pr[i]["price"])
    for i in range (len(tr)):
        transacted.append(tr[i]["transacted"])
    data = zip(symbol,share,price,transacted)
    return render_template("history.html", data=data)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    
    if request.method == "POST":
        result = lookup(request.form.get("symbol"))
        if result is None:
            return apology("invalid stock")
        return render_template("quoted.html", name=result["name"], symbol=result["symbol"], price=result["price"])
    else:
      return render_template("quote.html")  

    

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")
            
        elif not request.form.get("password2"):
            return apology("must re-enter password")
            
        if request.form.get("password")!=request.form.get("password2"):
             return apology("passwords do not match")
        
        hash = pwd_context.hash(request.form.get("password"))
        
        result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", username=request.form.get("username"), hash=hash)
        if not result:
            return apology("username already exists")
        
        session["user_id"] = result
        
        return redirect(url_for("index"))

    else:    
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    if request.method == "POST":
        stock = lookup(request.form.get("symbol"));
        if stock is None:
            return apology("invalid stock")
        amount = request.form.get("shares");
        sy = db.execute("SELECT shares FROM portfolio WHERE id = :id AND symbol=:symbol", id= session['user_id'], symbol=request.form.get("symbol"))
        if not sy:
            return apology("You don't own that stock")
        if not amount.isdigit() or (int(amount))%1!=0 or (int(amount))<=0 or int(amount)>sy[0]["shares"]:
            return apology("invalid shares")
        if (sy[0]["shares"]==int(amount)):
            db.execute("DELETE from 'portfolio' WHERE id = :id AND symbol=:symbol",id= session['user_id'], symbol=request.form.get("symbol") )
        else:
            db.execute("UPDATE 'portfolio' SET shares=:shares WHERE id=:id AND symbol=:symbol", shares=sy[0]["shares"]-int(request.form.get("shares")), id=session['user_id'], symbol=request.form.get("symbol"))
        db.execute("INSERT INTO history (id, symbol, shares, price) VALUES(:id, :symbol, :shares, :price)", id= session['user_id'], symbol=request.form.get("symbol"), shares=-int(request.form.get("shares")), price=stock["price"])
        profit = float(stock["price"])*float(amount)
        temp = db.execute("SELECT cash FROM users WHERE id=:id",id= session['user_id'])
        db.execute("UPDATE 'users' SET cash=:cash WHERE id=:id", cash=temp[0]["cash"]+profit, id= session['user_id'])
        return redirect(url_for("index"))
        
    else:
        return render_template("sell.html")


@app.route("/changepass", methods=["GET", "POST"])
@login_required
def changepass():
    """Change password."""
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("oldpass"):
            return apology("must provide current password")
        
        # ensure password was submitted
        elif not request.form.get("newpass"):
            return apology("must provide new password")
            
        elif not request.form.get("newpass2"):
            return apology("must re-enter new password")
        
        oldpasscheck = db.execute("SELECT hash FROM users WHERE id = :id", id= session['user_id'])
        
        if not pwd_context.verify(request.form.get("oldpass"), oldpasscheck[0]["hash"]):
            return apology("that is not your current password")
            
        if request.form.get("newpass")!=request.form.get("newpass2"):
             return apology("your new passwords do not match")
        
        hashed = pwd_context.hash(request.form.get("newpass"))
        
        db.execute("UPDATE 'users' SET hash=:hash WHERE id=:id", hash=hashed, id= session['user_id'])
        
        return redirect(url_for("index"))

    else:    
        return render_template("changepass.html")