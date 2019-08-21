import os

from cs50 import SQL
from flask import Flask, flash, jsonify, json, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, represents_int

from pprint import pprint

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    
    stocks = get_user_stocks()
    user = {}
    
    user["balance"] = db.execute("SELECT cash FROM users WHERE id = :id",
                                 id=session["user_id"])[0]["cash"]
    user["holdings"] = 0
    for k in stocks.keys():
        user["holdings"] += stocks[k]["value"]
    
    return render_template("index.html", user=user, stocks=stocks)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
        
    if request.method == "POST":        
        stock_quote = lookup(request.form.get("symbol"))
        if not stock_quote:
            return apology("Invalid stock symbol", 400)
        
        req = request.form
        
        if not represents_int(req.get("shares")) or int(req.get("shares")) < 0:
            return apology("Invalid number of shares")
        
        if stock_quote:
            user = db.execute("SELECT * FROM users WHERE id = :id",
                              id=session["user_id"])[0]
            
            pprint(req)
            
            if user["cash"] - (stock_quote["price"] * int(req.get("shares"))) < 0:
                return apology("Not enough money for purchase")
            
            sql = ("INSERT INTO transactions (user_id, type, quantity, symbol, price, total)" 
                   " VALUES (:user_id, :type, :quantity, :symbol, :price, :total)")
            transaction_id = db.execute(sql,
                                        user_id=user["id"], type="buy", quantity=int(req.get("shares")), 
                                        symbol=stock_quote["symbol"], price=stock_quote["price"],
                                        total=stock_quote["price"] * int(req.get("shares")))
            
            transaction = db.execute("SELECT * FROM transactions WHERE id=:id",
                                     id=transaction_id)[0]
            
            db.execute("UPDATE users SET cash=:cash WHERE id=:id", 
                       cash=(user["cash"] - transaction["total"]), id=user["id"])
            
            return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    
    # Check if username has correct length
    if len(request.args.get("username")) < 1:
        return json.dumps(False)
    
    if not request.args.get("username").isalnum():
        return json.dumps(False)
    
    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE username = :username",
                      username=request.args.get("username"))

    # Check if username already exists
    if len(rows) != 0:
        return json.dumps(False)
    
    return json.dumps(True)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    rows = db.execute("SELECT * FROM transactions WHERE user_id=:user_id",
                      user_id=session["user_id"])
    return render_template("history.html", transactions=rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/account", methods=["GET"])
@login_required
def account():
    user = db.execute("SELECT * FROM users WHERE id=:id",
                      id=session["user_id"])[0]

    return render_template("account.html", user=user)


@app.route("/password_change", methods=["POST"])
@login_required
def password_change():
    password = request.form.get("password")
    
    if not password:
        flash("Password must not be empty!", "danger")
        return redirect("/account")
    
    if len(password) < 4:
        flash("Password must be at least 4 characters. (Should be 8, 4 just for testing)", 
              "danger")
        return redirect("/account")
    
    pwd_hash = generate_password_hash(password)
    
    db.execute("UPDATE users SET hash=:pwd_hash WHERE id=:user_id",
               pwd_hash=pwd_hash, user_id=session["user_id"])
    
    flash("Password successfully changed!", "success")
    return redirect("/account")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        stock_quote = lookup(request.form.get("symbol"))
        if stock_quote:
            return render_template("quoted.html", name=stock_quote["name"], symbol=stock_quote["symbol"],
                                   price=usd(stock_quote["price"]))
        else:
            return apology(f"Could not get quote for symbol: {request.form.get('symbol')}")
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    '''register user'''
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 400)

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Check if username already exists
        if len(rows) != 0:
            return apology("username already exists", 400)
        else:
            pwd_hash = generate_password_hash(request.form.get("password"))
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                       username=request.form.get("username"), hash=pwd_hash)
        
        # Query database for registered username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        
        # Remember which user has registered and log them in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        req = request.form
        stocks = get_user_stocks()
        
        if req.get("symbol") not in stocks.keys():
            return apology("Invalid stock symbol")
        if not represents_int(req.get("shares")):
            return apology("Invalid number of shares")
        if (int(req.get("shares")) > stocks[req.get("symbol")]["quantity"] 
                or int(req.get("shares")) < 1):
            return apology("Invalid number of shares")
        
        user = db.execute("SELECT * FROM users WHERE id = :id",
                          id=session["user_id"])[0]
        stock_quote = lookup(req.get("symbol"))
           
        sql = ("INSERT INTO transactions (user_id, type, quantity, symbol, price, total)"
               " VALUES (:user_id, :type, :quantity, :symbol, :price, :total)")
        transaction_id = db.execute(sql,
                                    user_id=user["id"], type="sell", quantity=int(req.get("shares")), 
                                    symbol=stock_quote["symbol"], price=stock_quote["price"],
                                    total=stock_quote["price"] * int(req.get("shares")))
        
        transaction = db.execute("SELECT * FROM transactions WHERE id=:id",
                                 id=transaction_id)[0]
        
        db.execute("UPDATE users SET cash=:cash WHERE id=:id", 
                   cash=(user["cash"] + transaction["total"]), id=user["id"])
        
        return redirect("/")   
    else:
        return render_template("sell.html", stocks=get_user_stocks())
        

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


def get_user_stocks():
    """Get stocks owned by current user"""
    
    stocks = {}
    buys = db.execute("SELECT * FROM transactions WHERE user_id=:user_id AND type=:type",
                      user_id=session["user_id"], type="buy")
    sells = db.execute("SELECT * FROM transactions WHERE user_id=:user_id AND type=:type",
                       user_id=session["user_id"], type="sell")
    
    for buy in buys:
        try:
            stocks[buy["symbol"]]["quantity"] += buy["quantity"]
        except KeyError:
            stocks[buy["symbol"]] = {}
            stocks[buy["symbol"]]["quantity"] = buy["quantity"]            
    for sell in sells:
        try:
            stocks[sell["symbol"]]["quantity"] -= sell["quantity"]
        except KeyError:
            continue
    remove_keys = []    
    for k, v in stocks.items():
        if v["quantity"] == 0:
            remove_keys.append(k)
            continue
        v["price"] = lookup(k)["price"]
        v["value"] = v["quantity"] * v["price"]
    for k in remove_keys:
        stocks.pop(k)
    
    return stocks


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
